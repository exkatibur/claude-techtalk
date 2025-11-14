# InitAuth - Complete Authentication Setup

Complete command series to set up authentication for Flutter + Supabase apps using Clean Architecture.

## Overview

This is a **3-step command series** to go from zero to fully working authentication:

1. **Supabase Initialization** - Set up backend
2. **Auth Feature Implementation** - Build auth with Clean Architecture
3. **Navigation Setup** - Protect routes and handle auth flow

## Commands (Run in Order)

### 01 - Supabase Init
```bash
/initauth/01-supabase-init
```

**What it does:**
- Creates Supabase project
- Sets up database schema (user_profiles + app tables)
- Configures RLS policies
- Creates storage buckets
- Sets up `.env` file
- Initializes Supabase service in Flutter

**Duration:** ~30-45 minutes

---

### 02 - Auth Setup
```bash
/initauth/02-auth-setup
```

**What it does:**
- Creates auth feature (12+ files)
- Implements Clean Architecture (data/domain/presentation)
- Sets up Riverpod state management
- Creates login/signup pages
- Implements error handling
- Adds use cases (SignIn, SignUp, SignOut)

**Duration:** ~1-2 hours (mostly automated)

**After completion:** Run `flutter pub run build_runner build`

---

### 03 - Setup Navigation
```bash
/initauth/03-setup-navigation
```

**What it does:**
- Configures `go_router` with auth guards
- Sets up route protection
- Implements auth redirect logic
- Configures deep linking
- Creates route constants

**Duration:** ~30-45 minutes

---

## Quick Start

**First time setup:**
```bash
# 1. Initialize Supabase backend
/initauth/01-supabase-init

# 2. Build auth feature
/initauth/02-auth-setup

# 3. Generate code
flutter pub run build_runner build --delete-conflicting-outputs

# 4. Set up navigation
/initauth/03-setup-navigation

# 5. Test!
flutter run
```

## What You Get

After completing all 3 commands:

✅ **Backend:**
- Supabase project with database
- User authentication
- Row Level Security
- Storage buckets

✅ **Frontend:**
- Complete auth feature (Clean Architecture)
- Login/Signup pages
- State management (Riverpod)
- Protected routes
- Auth persistence

✅ **Ready for:**
- Building main app features
- Adding more routes
- Implementing business logic
- Deploying to production

## Tech Stack

- **Flutter** - Cross-platform framework
- **Supabase** - Backend (auth, database, storage)
- **Riverpod** - State management
- **go_router** - Navigation
- **Clean Architecture** - Project structure

## File Structure After Completion

```
your_app/
├── .env                                    # API keys (gitignored)
├── lib/
│   ├── app/
│   │   └── routes/
│   │       ├── app_router.dart            # Navigation config
│   │       └── route_names.dart           # Route constants
│   ├── core/
│   │   ├── errors/
│   │   │   └── failures.dart              # Error handling
│   │   └── services/
│   │       └── supabase_service.dart      # Supabase client
│   └── features/
│       └── auth/
│           ├── data/
│           │   ├── datasources/
│           │   │   └── auth_remote_datasource.dart
│           │   ├── models/
│           │   │   └── user_model.dart
│           │   └── repositories/
│           │       └── auth_repository_impl.dart
│           ├── domain/
│           │   ├── entities/
│           │   │   └── user.dart
│           │   ├── repositories/
│           │   │   └── auth_repository.dart
│           │   └── usecases/
│           │       ├── sign_in.dart
│           │       ├── sign_up.dart
│           │       ├── sign_out.dart
│           │       └── get_current_user.dart
│           └── presentation/
│               ├── pages/
│               │   ├── login_page.dart
│               │   └── signup_page.dart
│               ├── widgets/
│               │   └── auth_form.dart
│               └── providers/
│                   └── auth_provider.dart
```

## Customization

Each command is **generic** and adapts to your project:
- Uses your app's naming conventions
- Adapts to existing file structure
- Allows custom table schemas
- Supports app-specific routes

## Common Questions

**Q: Can I skip step 1 if I already have Supabase?**
A: Yes, but ensure you have `user_profiles` table and RLS policies set up.

**Q: Can I use BLoC instead of Riverpod?**
A: Yes, modify step 2 to use BLoC. The architecture stays the same.

**Q: Do I need all 3 commands?**
A: Technically no, but they're designed to work together. Each builds on the previous.

**Q: Can I use this for multiple apps?**
A: Absolutely! That's why it's generalized.

## Troubleshooting

**Command fails at step 2:**
- Ensure step 1 completed successfully
- Check `.env` file exists and has correct keys
- Verify Supabase project is accessible

**Code generation fails:**
- Run `flutter pub get` first
- Ensure `build_runner` is in `dev_dependencies`
- Clear cache: `flutter pub run build_runner clean`

**Navigation doesn't redirect:**
- Check auth state in provider
- Verify `routerProvider` watches `authNotifierProvider`
- Test auth state changes manually

## Next Steps After Setup

1. **Build your main features** - Auth is done, focus on your app logic
2. **Add more routes** - Use the same pattern in `app_router.dart`
3. **Implement password reset** - Add to step 2 if needed
4. **Add social logins** - Apple, Google (extend step 1 & 2)
5. **Deploy** - Use Supabase Edge Functions, Stripe, etc.

## Support

Issues? Check:
1. Each command's "Prerequisites" section
2. Each command's "Post-Setup Tasks" checklist
3. Supabase dashboard logs
4. Flutter error messages

---

**Happy building! 🚀**
