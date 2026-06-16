#!/usr/bin/env bash
# project-check.sh — Auto-detect project type and run quality checks.
# Exit 0 if all checks pass, non-zero otherwise.

set -uo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT" || { echo "Cannot cd to $REPO_ROOT"; exit 1; }

PASS=0
FAIL=0
BLOCKERS=""

log() { echo "[project-check] $*"; }
run_cmd() {
  local cmd="$1"
  local label="$2"
  log "Running: $label"
  if eval "$cmd"; then
    log "✓ $label passed"
    PASS=$((PASS + 1))
  else
    log "✗ $label failed"
    FAIL=$((FAIL + 1))
    BLOCKERS="$BLOCKERS\n- $label"
  fi
}

# Project-level override
if [[ -x scripts/project-check ]]; then
  log "Using project-level scripts/project-check"
  ./scripts/project-check
  exit $?
fi

if [[ -f Makefile ]] && grep -qE "^[a-zA-Z0-9_-]+:.*#?.*trellis" Makefile; then
  log "Using Makefile trellis target"
  make project-check
  exit $?
fi

# Helper: detect conda env name
conda_env() {
  if [[ -n "${CONDA_DEFAULT_ENV:-}" ]]; then
    echo "$CONDA_DEFAULT_ENV"
  elif [[ -f environment.yml ]]; then
    head -1 environment.yml | sed 's/name: //'
  else
    echo ""
  fi
}

run_python_checks() {
  local env="$(conda_env)"
  local prefix=""
  if [[ -n "$env" ]]; then
    prefix="conda run -n $env "
  fi

  if command -v ruff >/dev/null 2>&1; then
    run_cmd "${prefix}ruff check ." "Python lint (ruff)"
  elif command -v flake8 >/dev/null 2>&1; then
    run_cmd "${prefix}flake8 ." "Python lint (flake8 fallback)"
  else
    run_cmd "${prefix}python -m compileall ." "Python syntax check"
  fi

  if [[ -f pyproject.toml ]] && command -v mypy >/dev/null 2>&1; then
    run_cmd "${prefix}mypy ." "Python type check (mypy)"
  fi

  if command -v pytest >/dev/null 2>&1; then
    run_cmd "${prefix}pytest" "Python tests (pytest)"
  fi
}

run_node_checks() {
  if [[ -f package.json ]]; then
    if npm run --silent lint >/dev/null 2>&1; then
      run_cmd "npm run lint" "Node lint"
    elif npx eslint . >/dev/null 2>&1; then
      run_cmd "npx eslint ." "Node lint (eslint fallback)"
    fi

    if npm run --silent test >/dev/null 2>&1; then
      run_cmd "npm run test" "Node tests"
    fi
  fi
}

run_rust_checks() {
  if command -v cargo >/dev/null 2>&1; then
    run_cmd "cargo check" "Rust check"
    run_cmd "cargo test" "Rust tests"
  fi
}

run_go_checks() {
  if command -v go >/dev/null 2>&1; then
    run_cmd "go vet ./..." "Go vet"
    run_cmd "go test ./..." "Go tests"
  fi
}

run_java_checks() {
  if [[ -f pom.xml ]] && command -v mvn >/dev/null 2>&1; then
    run_cmd "mvn test" "Java (maven) tests"
  elif [[ -f build.gradle ]] && [[ -x ./gradlew ]]; then
    run_cmd "./gradlew test" "Java (gradle) tests"
  fi
}

run_ruby_checks() {
  if command -v bundle >/dev/null 2>&1; then
    run_cmd "bundle exec rubocop" "Ruby lint"
    run_cmd "bundle exec rspec" "Ruby tests"
  fi
}

run_elixir_checks() {
  if command -v mix >/dev/null 2>&1; then
    run_cmd "mix format --check-formatted" "Elixir format"
    run_cmd "mix test" "Elixir tests"
  fi
}

run_php_checks() {
  if command -v composer >/dev/null 2>&1; then
    if composer run --list | grep -q lint; then
      run_cmd "composer lint" "PHP lint"
    fi
    if composer run --list | grep -q test; then
      run_cmd "composer test" "PHP tests"
    fi
  fi
}

run_csharp_checks() {
  if command -v dotnet >/dev/null 2>&1; then
    run_cmd "dotnet test" "C# tests"
  fi
}

run_swift_checks() {
  if command -v swift >/dev/null 2>&1; then
    run_cmd "swift test" "Swift tests"
  fi
}

# Detect project types
DETECTED=()
[[ -f package.json ]] && DETECTED+=("node")
[[ -f pyproject.toml || -f requirements.txt ]] && DETECTED+=("python")
[[ -f Cargo.toml ]] && DETECTED+=("rust")
[[ -f go.mod ]] && DETECTED+=("go")
[[ -f pom.xml || -f build.gradle ]] && DETECTED+=("java")
[[ -f Gemfile ]] && DETECTED+=("ruby")
[[ -f mix.exs ]] && DETECTED+=("elixir")
[[ -f composer.json ]] && DETECTED+=("php")
[[ -n "$(find . -maxdepth 2 -name '*.csproj' -o -name '*.sln' | head -1)" ]] && DETECTED+=("csharp")
[[ -f Package.swift ]] && DETECTED+=("swift")

if [[ ${#DETECTED[@]} -eq 0 ]]; then
  log "No supported project type detected. Nothing to check."
  exit 0
fi

log "Detected project type(s): ${DETECTED[*]}"

for t in "${DETECTED[@]}"; do
  case "$t" in
    node) run_node_checks ;;
    python) run_python_checks ;;
    rust) run_rust_checks ;;
    go) run_go_checks ;;
    java) run_java_checks ;;
    ruby) run_ruby_checks ;;
    elixir) run_elixir_checks ;;
    php) run_php_checks ;;
    csharp) run_csharp_checks ;;
    swift) run_swift_checks ;;
  esac
done

log "Summary: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  echo -e "Failed checks:$BLOCKERS"
  exit 1
fi
exit 0
