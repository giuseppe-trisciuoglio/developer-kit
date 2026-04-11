#!/bin/bash
#
# Install pre-commit hooks for Claude Code Developer Kit validation.
#
# Usage: ./install-hooks.sh [--force]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOKS_DIR="${REPO_ROOT}/.git/hooks"
VALIDATOR_DIR="${REPO_ROOT}/.skills-validator-check"
FORCE=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--force]"
            echo "  --force  Overwrite existing hooks"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if we're in a git repository
if [[ ! -d "${REPO_ROOT}/.git" ]]; then
    log_error "Not a git repository. Please run from the repository root."
    exit 1
fi

# Check Python version
log_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    log_error "Python 3.8+ is required. Found: ${PYTHON_VERSION}"
    exit 1
fi
log_success "Python ${PYTHON_VERSION} detected"

# Install Python dependencies
log_info "Installing Python dependencies..."
if python3 -c "import yaml" 2>/dev/null; then
    log_success "PyYAML already installed"
else
    pip3 install --user pyyaml --quiet || {
        log_warn "pip install --user failed, trying without --user"
        pip3 install pyyaml --quiet || {
            log_error "Failed to install PyYAML"
            exit 1
        }
    }
    log_success "PyYAML installed"
fi

# Create hooks directory if needed
mkdir -p "${HOOKS_DIR}"

# Install pre-commit hook
PRE_COMMIT_HOOK="${HOOKS_DIR}/pre-commit"

if [[ -f "${PRE_COMMIT_HOOK}" ]] && [[ "${FORCE}" != "true" ]]; then
    log_warn "pre-commit hook already exists. Use --force to overwrite."
    log_warn "Current hook: $(head -1 "${PRE_COMMIT_HOOK}")"
else
    log_info "Installing pre-commit hook..."

    cat > "${PRE_COMMIT_HOOK}" << 'HOOK_EOF'
#!/bin/bash
# Auto-generated pre-commit hook for Claude Code Developer Kit
# Source: .skills-validator-check/pre-commit.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VALIDATOR="${REPO_ROOT}/.skills-validator-check/pre-commit.py"

if [[ -f "${VALIDATOR}" ]]; then
    python3 "${VALIDATOR}"
    exit $?
else
    echo "Warning: Validator not found at ${VALIDATOR}"
    exit 0
fi
HOOK_EOF

    chmod +x "${PRE_COMMIT_HOOK}"
    log_success "pre-commit hook installed"
fi

# Verify installation
log_info "Verifying installation..."
if python3 -c "import sys; sys.path.insert(0, '${VALIDATOR_DIR}'); from validators.cli import ValidationCLI" 2>/dev/null; then
    log_success "Validator package is importable"
else
    log_warn "Validator package import test failed - may still work"
fi

# Summary
echo ""
echo "========================================"
log_success "Installation complete!"
echo ""
echo "The pre-commit hook will now validate:"
echo "  - skills/**/SKILL.md files"
echo "  - agents/*.md files"
echo "  - .claude/commands/*.md files"
echo ""
echo "Manual validation:"
echo "  python3 ${VALIDATOR_DIR}/validators/cli.py --all"
echo ""
echo "To bypass validation: git commit --no-verify"
echo "To uninstall: rm ${PRE_COMMIT_HOOK}"
echo "========================================"
