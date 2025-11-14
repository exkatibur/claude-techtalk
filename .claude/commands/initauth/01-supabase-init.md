# 01 - Supabase Initialization

Set up Supabase project, database schema, RLS policies, and environment configuration for a Flutter app.

## What This Command Does

1. Guides you through Supabase project creation
2. Creates all necessary database tables
3. Sets up Row Level Security (RLS) policies
4. Configures Storage buckets
5. Sets up authentication providers
6. Creates `.env` configuration file

## Prerequisites

- Supabase account (free tier is fine)
- Project name decided
- Region preference known

## Database Tables to Create

### 1. User Profiles Table
Extends Supabase auth.users with app-specific data:
- `id` (UUID, references auth.users)
- `email` (TEXT)
- `full_name` (TEXT)
- `avatar_url` (TEXT)
- `is_premium` (BOOLEAN)
- `subscription_status` (TEXT)
- `subscription_id` (TEXT)
- `subscription_expires_at` (TIMESTAMPTZ)
- `created_at`, `updated_at` (TIMESTAMPTZ)

**With RLS policies and auto-creation trigger**

### 2. Additional Tables
Depends on app requirements. Common examples:
- `rooms` / `categories` - Organization entities
- `items` / `content` - Main app content
- `user_preferences` - Settings
- `activity_log` - Audit trail

## Storage Buckets

Create buckets based on app needs:
- `user-uploads` - User-uploaded images/files
- `avatars` - Profile pictures
- `public-assets` - Public accessible files

**With RLS policies for user isolation**

## SQL Scripts to Execute

### Enable Extensions
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### User Profiles Table
```sql
CREATE TABLE public.user_profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  is_premium BOOLEAN DEFAULT FALSE,
  subscription_status TEXT DEFAULT 'free',
  subscription_id TEXT,
  subscription_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
  ON public.user_profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.user_profiles FOR UPDATE
  USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, full_name)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### Updated At Trigger (Apply to All Tables)
```sql
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

## Storage Setup

### Create Bucket (Example: user-uploads)
```sql
-- Via SQL Editor
INSERT INTO storage.buckets (id, name, public)
VALUES ('user-uploads', 'user-uploads', false);
```

### Storage Policies
```sql
-- Users can upload to their own folder
CREATE POLICY "Users can upload own files"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'user-uploads' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can view own files
CREATE POLICY "Users can view own files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'user-uploads' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can delete own files
CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'user-uploads' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

## Environment Configuration

### Create `.env` File
```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here

# OpenAI (if using AI features)
OPENAI_API_KEY=your_openai_key_here

# Stripe (if using payments)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### Update `.gitignore`
```
.env
*.env
.env.local
```

## Authentication Configuration

1. Go to **Authentication** → **Providers** in Supabase Dashboard
2. **Email Provider**: Enabled by default
3. **Email Confirmation**: Consider disabling for development
4. Optional providers:
   - Apple Sign-In (recommended for iOS apps)
   - Google OAuth
   - Magic Link

## Create Todo List After Completion

After running this command, create a checklist:

**Supabase Setup Checklist:**
- [ ] Supabase project created
- [ ] Database tables created (user_profiles + app-specific)
- [ ] RLS policies applied to all tables
- [ ] Storage buckets created
- [ ] Storage policies configured
- [ ] Auth providers configured
- [ ] `.env` file created with API keys
- [ ] `.env` added to `.gitignore`
- [ ] API keys tested (can connect from Flutter app)
- [ ] Ready for Step 2: Auth Setup

## Flutter Integration

Create `lib/core/services/supabase_service.dart`:

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class SupabaseService {
  static Future<void> initialize() async {
    await Supabase.initialize(
      url: dotenv.env['SUPABASE_URL']!,
      anonKey: dotenv.env['SUPABASE_ANON_KEY']!,
    );
  }

  static SupabaseClient get client => Supabase.instance.client;
}
```

Initialize in `main.dart`:
```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await dotenv.load(fileName: ".env");
  await SupabaseService.initialize();

  runApp(const MyApp());
}
```

## Verification

Test connection in Flutter:
```dart
final response = await SupabaseService.client
  .from('user_profiles')
  .select()
  .limit(1);
print('Connection successful: $response');
```

## Notes

- Start with minimal schema, add tables as needed
- RLS is CRITICAL - never skip it
- Use meaningful table/column names
- Document complex SQL functions
- Keep `.env` secure and never commit it
- Consider using Supabase CLI for version control of schema changes

## Resources

- [Supabase Dashboard](https://supabase.com/dashboard)
- [Supabase Flutter Docs](https://supabase.com/docs/reference/dart/introduction)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## Next Command

After completion, run: `/initauth/02-auth-setup`
