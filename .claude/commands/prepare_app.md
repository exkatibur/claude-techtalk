# Prepare App

Bereitet die Flutter App für Testing, Validation oder Review vor.

## Variables

- **FLUTTER_DEVICE**: If provided, use this device (e.g., "chrome", "android", "ios"). Otherwise, prepare for headless testing.
- **TARGET_DIR**: If `.env` exists and has `FLUTTER_APP_DIR`, use that. Otherwise, auto-detect `TidySnap/` or `tidy-snap-flutter/`.

## Setup

### 1. Navigate to Flutter Project

Check for Flutter project directory:
```bash
if [ -d "TidySnap" ]; then
  cd TidySnap
elif [ -d "tidy-snap-flutter" ]; then
  cd tidy-snap-flutter
else
  echo "❌ No Flutter project found"
  exit 4
fi
```

### 2. Install Dependencies

Run Flutter pub get to ensure all packages are installed:
```bash
flutter pub get
```

**Expected**: Exit code 0, output includes "Running 'flutter pub get'..."

**On Error**:
- Exit code != 0 → Check `pubspec.yaml` for syntax errors
- "version solving failed" → Document conflicting packages
- "SDK version" → Display required Flutter version

### 3. Code Generation (if needed)

Check if `build_runner` is used:
```bash
grep -q "build_runner" pubspec.yaml
```

If found, run code generation:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**Expected**: Exit code 0, generates `*.g.dart` files

**On Error**: Document specific build_runner error for user

### 4. Verify Environment Configuration

Check for Supabase configuration:
```bash
if [ -f ".env" ] || [ -f "lib/core/config/supabase_config.dart" ]; then
  echo "✅ Supabase configuration found"
else
  echo "⚠️  WARNING: No Supabase configuration found"
  echo "   Apps using Supabase require configuration"
fi
```

### 5. Run Static Analysis

Perform Flutter analyze to check code quality:
```bash
flutter analyze --no-pub
```

**Interpretation**:
- "No issues found!" → ✅ Code is clean
- Warnings/Infos → ⚠️ Document but don't block
- Errors → 🚫 Must be fixed before tests

### 6. Verify Application is Ready

Check that the app can be built (without actually building):
```bash
flutter doctor --verbose
```

**Expected**: All required components available

**Output Summary**:
```
📱 Flutter App Preparation Complete

✅ Project found: TidySnap/
✅ Dependencies installed (X packages)
✅ Code generated (if applicable)
✅ Supabase configured
✅ Static analysis clean (Y warnings)
✅ Flutter doctor checks passed

App is ready for: Testing, Review, or Execution
Device: ${FLUTTER_DEVICE:-headless}
```

## Usage in Agents

This command is invoked by:
- **app-validator**: Before running test suite
- **spec-implementation-reviewer**: Before taking screenshots
- **e2e-test-executor**: Before executing integration tests

Example from agent:
```markdown
Before executing tests, prepare the app:
Use SlashCommand tool: /prepare_app
```

## Error Scenarios

### Flutter SDK Not Installed
```
command not found: flutter
```
**Solution**: Install Flutter SDK from https://flutter.dev and add to PATH

### Outdated Dependencies
```
Some dependencies are outdated
```
**Solution**: Run `flutter pub upgrade` (requires user confirmation)

### Build Runner Failure
```
[SEVERE] Failed to build
```
**Solution**:
- Check syntax in source files
- Delete `build/` directory: `rm -rf build/`
- Retry code generation
- Document specific error for user

### No Flutter Project Found
```
❌ No Flutter project found
```
**Solution**: Verify you're in the Kassiopeia repository root directory

## Exit Codes

- **0**: App successfully prepared, ready for testing
- **1**: Dependencies could not be installed
- **2**: Code generation failed
- **3**: Static analysis shows errors
- **4**: No Flutter project found

## Notes

- This command is **idempotent** - can be run multiple times safely
- Typical execution time: 5-15 seconds
- For web target: Ensure `flutter config --enable-web` is set
- Read `TidySnap/README.md` or `tidy-snap-flutter/README.md` for more information on running the app
- For actual app execution (not just prep), use `flutter run -d ${FLUTTER_DEVICE}`
