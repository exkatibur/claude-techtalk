# 02 - Auth Setup - Flutter + Supabase

Set up complete Supabase authentication following Clean Architecture pattern.

## Prerequisites

Before running this command, ensure:
- [ ] Supabase project is set up (run `/initauth/01-supabase-init` first)
- [ ] `.env` file exists with SUPABASE_URL and SUPABASE_ANON_KEY
- [ ] `user_profiles` table exists in Supabase
- [ ] Flutter dependencies installed: `supabase_flutter`, `riverpod`, `go_router`
- [ ] `lib/core/services/supabase_service.dart` exists
- [ ] `lib/core/errors/failures.dart` exists or will be created

## Tech Stack
- **Flutter** (cross-platform mobile)
- **Supabase** (auth.users + JWT)
- **Riverpod** (state management)
- **Clean Architecture** (data/domain/presentation layers)

## File Structure to Create

```
lib/features/auth/
├── data/
│   ├── datasources/
│   │   └── auth_remote_datasource.dart       # Supabase auth API calls
│   ├── models/
│   │   └── user_model.dart                   # JSON serialization
│   └── repositories/
│       └── auth_repository_impl.dart         # Repository implementation
├── domain/
│   ├── entities/
│   │   └── user.dart                         # Pure Dart entity
│   ├── repositories/
│   │   └── auth_repository.dart              # Repository contract
│   └── usecases/
│       ├── sign_in.dart                      # Login use case
│       ├── sign_up.dart                      # Register use case
│       ├── sign_out.dart                     # Logout use case
│       └── get_current_user.dart             # Get logged-in user
└── presentation/
    ├── pages/
    │   ├── login_page.dart                   # Login UI
    │   └── signup_page.dart                  # Registration UI
    ├── widgets/
    │   └── auth_form.dart                    # Reusable form widget
    └── providers/
        └── auth_provider.dart                # Riverpod state management
```

## Implementation Requirements

### 1. Domain Layer (Pure Dart - No Dependencies)

**`domain/entities/user.dart`:**
```dart
class User {
  final String id;
  final String email;
  final String? fullName;
  final String? avatarUrl;
  final bool isPremium;
  final DateTime createdAt;
}
```

**`domain/repositories/auth_repository.dart`:**
```dart
abstract class AuthRepository {
  Future<Either<Failure, User>> signUp({required String email, required String password, String? fullName});
  Future<Either<Failure, User>> signIn({required String email, required String password});
  Future<Either<Failure, void>> signOut();
  Future<Either<Failure, User?>> getCurrentUser();
  Stream<User?> get authStateChanges;
}
```

**Use Cases:**
- Each use case = single responsibility
- Return `Either<Failure, T>` for error handling
- Example: `SignIn`, `SignUp`, `SignOut`, `GetCurrentUser`

### 2. Data Layer (Supabase Integration)

**`data/datasources/auth_remote_datasource.dart`:**
```dart
abstract class AuthRemoteDataSource {
  Future<UserModel> signUp({required String email, required String password, String? fullName});
  Future<UserModel> signIn({required String email, required String password});
  Future<void> signOut();
  Future<UserModel?> getCurrentUser();
  Stream<UserModel?> get authStateChanges;
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final SupabaseClient supabase;

  // Use Supabase auth methods:
  // - supabase.auth.signUp()
  // - supabase.auth.signInWithPassword()
  // - supabase.auth.signOut()
  // - supabase.auth.currentUser
  // - supabase.auth.onAuthStateChange
}
```

**`data/models/user_model.dart`:**
```dart
class UserModel extends User {
  // fromJson() - Parse Supabase auth.users response
  // toJson() - Serialize for storage
  // Also fetch user_profiles table data if needed
}
```

**`data/repositories/auth_repository_impl.dart`:**
- Implements `AuthRepository`
- Calls `AuthRemoteDataSource`
- Converts `UserModel` → `User` entity
- Handles errors and returns `Either<Failure, T>`

### 3. Presentation Layer (UI + State)

**`presentation/providers/auth_provider.dart`:**
```dart
@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  AsyncValue<User?> build() {
    // Listen to auth state changes
    // Return current user or null
  }

  Future<void> signIn(String email, String password) async {
    // Call SignIn use case
    // Update state
  }

  Future<void> signUp(String email, String password, String? fullName) async {
    // Call SignUp use case
    // Update state
  }

  Future<void> signOut() async {
    // Call SignOut use case
    // Update state
  }
}
```

**`presentation/pages/login_page.dart`:**
- Email/password form
- Validation (email format, password length)
- Loading states
- Error messages
- Navigation to home on success

**`presentation/pages/signup_page.dart`:**
- Email/password/fullName form
- Password confirmation
- Terms & conditions checkbox
- Error handling

### 4. Error Handling

**`core/errors/failures.dart`:**
```dart
abstract class Failure {
  final String message;
}

class AuthFailure extends Failure {
  AuthFailure(String message) : super(message);
}

class NetworkFailure extends Failure {
  NetworkFailure(String message) : super(message);
}
```

**Error Types to Handle:**
- Invalid email format
- Weak password (< 6 characters)
- Email already registered
- Invalid credentials (wrong password)
- Network errors
- Supabase session expired

### 5. Token Management (Automatic via Supabase)

Supabase Flutter SDK handles tokens automatically:
- Access token stored securely
- Auto-refresh on expiry
- Persisted across app restarts
- No manual JWT handling needed!

### 6. Authentication Flow

```
App Start → Check Supabase Session
  ├─ Session exists → Navigate to Home
  └─ No session → Navigate to Login

Login → Supabase.signInWithPassword()
  ├─ Success → User entity, navigate to Home
  └─ Error → Show error message

Sign Up → Supabase.signUp()
  ├─ Success → Auto-login, navigate to Home
  └─ Error → Show error message

Sign Out → Supabase.signOut()
  └─ Clear session, navigate to Login
```

### 7. Integration with App Features

**After auth is set up:**
- User ID available: `Supabase.instance.client.auth.currentUser?.id`
- Use for Row Level Security (RLS) in database queries
- Attach to all API calls automatically
- All user data filtered by `user_id` automatically via RLS

### 8. Testing

Create these test files:
- `test/features/auth/data/datasources/auth_remote_datasource_test.dart`
- `test/features/auth/data/repositories/auth_repository_impl_test.dart`
- `test/features/auth/domain/usecases/sign_in_test.dart`

Mock Supabase client for unit tests.

## Auth Methods to Support

**For MVP:**
- ✅ Email/Password (Primary)

**Future (Post-MVP):**
- Apple Sign-In (required for App Store if offering other social logins)
- Google OAuth
- Magic Link (passwordless)

## Additional Features

- [ ] Email verification (optional for MVP)
- [ ] Password reset flow
- [ ] Remember me (auto-handled by Supabase)
- [ ] Biometric authentication (future)

## Post-Setup Tasks

After this command completes, create a todo list:

**Auth Setup Completion Checklist:**
- [ ] All 12+ auth files created
- [ ] Run code generation: `flutter pub run build_runner build --delete-conflicting-outputs`
- [ ] Check for compilation errors: `flutter analyze`
- [ ] Set up navigation with auth redirect (see next command: `/initauth/03-setup-navigation`)
- [ ] Test signup flow manually
- [ ] Test login flow manually
- [ ] Test logout flow manually
- [ ] Test auth persistence (restart app while logged in)
- [ ] Create unit tests for use cases
- [ ] Document any app-specific auth requirements

## Notes

- Follow project's existing Clean Architecture structure
- Use Riverpod code generation (`@riverpod` annotations)
- All auth state persists automatically via Supabase
- Ensure RLS policies are set up in Supabase (should be done in step 01)
- JWT tokens managed automatically by Supabase SDK
- No need for manual token refresh logic
- Adapt naming conventions to match existing project structure

## Next Command

After completion, run: `/initauth/03-setup-navigation`
