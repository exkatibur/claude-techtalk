# 03 - Setup Navigation with Auth

Set up `go_router` navigation with authentication guards, deep linking, and route protection.

## Prerequisites

Before running this command:
- [ ] Auth feature is complete (run `/initauth/02-auth-setup` first)
- [ ] `go_router` package installed in `pubspec.yaml`
- [ ] Auth provider exists: `lib/features/auth/presentation/providers/auth_provider.dart`
- [ ] Main pages exist (login, signup, home/dashboard)

## What This Command Does

1. Creates `app_router.dart` with `go_router` configuration
2. Sets up auth redirect logic (logged-in → home, logged-out → login)
3. Configures route guards for protected routes
4. Sets up deep linking support
5. Handles navigation from auth state changes
6. Creates route constants for type safety

## File Structure to Create

```
lib/app/routes/
├── app_router.dart              # Main router configuration
├── route_names.dart             # Route constants
└── guards/
    └── auth_guard.dart          # Route protection logic (optional)
```

## Implementation

### 1. Route Names (Type Safety)

**`lib/app/routes/route_names.dart`:**
```dart
class RouteNames {
  // Auth routes
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';

  // Main app routes
  static const String home = '/';
  static const String profile = '/profile';
  static const String settings = '/settings';

  // Add your app-specific routes here
}
```

### 2. Router Configuration

**`lib/app/routes/app_router.dart`:**
```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/presentation/providers/auth_provider.dart';
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/signup_page.dart';
import 'route_names.dart';

// Provider for the router
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: RouteNames.home,
    debugLogDiagnostics: true,

    // Auth redirect logic
    redirect: (context, state) {
      final isLoggedIn = authState.value != null;
      final isAuthRoute = state.matchedLocation.startsWith('/login') ||
          state.matchedLocation.startsWith('/signup');

      // If not logged in and trying to access protected route → login
      if (!isLoggedIn && !isAuthRoute) {
        return RouteNames.login;
      }

      // If logged in and trying to access auth route → home
      if (isLoggedIn && isAuthRoute) {
        return RouteNames.home;
      }

      // No redirect needed
      return null;
    },

    // Route configuration
    routes: [
      // Auth Routes (Public)
      GoRoute(
        path: RouteNames.login,
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: RouteNames.signup,
        name: 'signup',
        builder: (context, state) => const SignupPage(),
      ),

      // Main App Routes (Protected)
      GoRoute(
        path: RouteNames.home,
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: RouteNames.profile,
        name: 'profile',
        builder: (context, state) => const ProfilePage(),
      ),
      GoRoute(
        path: RouteNames.settings,
        name: 'settings',
        builder: (context, state) => const SettingsPage(),
      ),

      // Add your app-specific routes here
    ],

    // Error handling
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Text('Page not found: ${state.uri}'),
      ),
    ),
  );
});
```

### 3. Integrate Router in App

**Update `lib/app/app.dart` (or `main.dart`):**
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'routes/app_router.dart';

class MyApp extends ConsumerWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Your App Name',
      theme: ThemeData(/* your theme */),
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
```

### 4. Navigation Helper Methods (Optional)

**`lib/core/utils/navigation_utils.dart`:**
```dart
import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';

class NavigationUtils {
  // Navigate to route
  static void goTo(BuildContext context, String route) {
    context.go(route);
  }

  // Push route (keeps previous in stack)
  static void pushTo(BuildContext context, String route) {
    context.push(route);
  }

  // Replace current route
  static void replaceTo(BuildContext context, String route) {
    context.replace(route);
  }

  // Go back
  static void goBack(BuildContext context) {
    context.pop();
  }

  // Navigate with named route
  static void goToNamed(BuildContext context, String name, {Map<String, String>? params}) {
    context.goNamed(name, pathParameters: params ?? {});
  }
}
```

### 5. Deep Linking Support

For deep linking (e.g., password reset links, email verification):

**Android (`android/app/src/main/AndroidManifest.xml`):**
```xml
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="yourapp" android:host="*" />
</intent-filter>
```

**iOS (`ios/Runner/Info.plist`):**
```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleTypeRole</key>
        <string>Editor</string>
        <key>CFBundleURLName</key>
        <string>com.yourcompany.yourapp</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>yourapp</string>
        </array>
    </dict>
</array>
```

**Handle deep links in router:**
```dart
GoRoute(
  path: '/reset-password/:token',
  name: 'reset-password',
  builder: (context, state) {
    final token = state.pathParameters['token']!;
    return ResetPasswordPage(token: token);
  },
),
```

### 6. Auth State Listener (Alternative Approach)

If you prefer listening to auth changes separately:

**`lib/app/app.dart`:**
```dart
class MyApp extends ConsumerStatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  ConsumerState<MyApp> createState() => _MyAppState();
}

class _MyAppState extends ConsumerState<MyApp> {
  @override
  void initState() {
    super.initState();

    // Listen to auth state changes
    ref.listenManual(authNotifierProvider, (previous, next) {
      // User logged in
      if (previous?.value == null && next.value != null) {
        // Navigate to home if needed
      }

      // User logged out
      if (previous?.value != null && next.value == null) {
        // Navigate to login if needed
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      routerConfig: router,
    );
  }
}
```

## Advanced Features

### Protected Routes with Custom Guards
```dart
GoRoute(
  path: '/admin',
  name: 'admin',
  redirect: (context, state) {
    // Check if user has admin role
    final user = ref.read(authNotifierProvider).value;
    if (user?.role != 'admin') {
      return RouteNames.home;
    }
    return null;
  },
  builder: (context, state) => const AdminPage(),
),
```

### Nested Navigation
```dart
GoRoute(
  path: '/dashboard',
  builder: (context, state) => const DashboardPage(),
  routes: [
    GoRoute(
      path: 'analytics',
      builder: (context, state) => const AnalyticsPage(),
    ),
    GoRoute(
      path: 'reports',
      builder: (context, state) => const ReportsPage(),
    ),
  ],
),
```

### Bottom Navigation Setup
```dart
final shellNavigatorKey = GlobalKey<NavigatorState>();

ShellRoute(
  navigatorKey: shellNavigatorKey,
  builder: (context, state, child) {
    return MainScaffold(child: child); // Your scaffold with bottom nav
  },
  routes: [
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/explore',
      builder: (context, state) => const ExplorePage(),
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfilePage(),
    ),
  ],
),
```

## Testing Navigation

**Test redirect logic:**
```dart
void main() {
  testWidgets('Redirects to login when not authenticated', (tester) async {
    // Mock auth state as logged out
    // Navigate to protected route
    // Verify redirected to login
  });

  testWidgets('Redirects to home when authenticated', (tester) async {
    // Mock auth state as logged in
    // Navigate to login page
    // Verify redirected to home
  });
}
```

## Post-Setup Tasks

After this command completes, create a todo list:

**Navigation Setup Checklist:**
- [ ] Router configuration created
- [ ] Route names defined
- [ ] Auth redirect logic working
- [ ] Test: Logged-out user accessing home → redirects to login
- [ ] Test: Logged-in user accessing login → redirects to home
- [ ] Test: Navigation between pages works
- [ ] Test: Back button behavior correct
- [ ] Deep linking configured (Android + iOS)
- [ ] Test deep links (if applicable)
- [ ] Bottom navigation setup (if applicable)
- [ ] Error page displays for invalid routes
- [ ] All routes documented in `route_names.dart`

## Common Issues & Solutions

**Issue**: Redirect loop (constantly redirecting between login/home)
**Solution**: Check `redirect` logic, ensure auth state is stable

**Issue**: Routes not found
**Solution**: Verify route paths match exactly (case-sensitive)

**Issue**: Deep links not working
**Solution**: Check manifest/Info.plist configuration, test with `adb` or Xcode

**Issue**: Navigation after logout doesn't work
**Solution**: Ensure auth state change triggers router rebuild

## Notes

- `go_router` automatically handles browser back button (web)
- Use `context.go()` for replacement, `context.push()` for stacking
- Named routes are type-safe and recommended
- Consider using `ShellRoute` for persistent UI (bottom nav, drawer)
- Test navigation thoroughly on all platforms

## Resources

- [go_router Documentation](https://pub.dev/packages/go_router)
- [Deep Linking Guide](https://docs.flutter.dev/development/ui/navigation/deep-linking)

## Completion

Your auth + navigation setup is now complete! 🎉

Next steps:
1. Build your main app features
2. Add more routes as needed
3. Implement password reset flow (optional)
4. Add social login providers (optional)
