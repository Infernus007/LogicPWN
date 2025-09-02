from .baseline import (
    _check_unauthenticated_baseline,
    _get_unauth_baseline,
    get_cached_unauth_baseline,
)
from .core_logic import (
    _determine_vulnerability,
    _make_request_with_retry,
    _should_have_access,
    _test_single_id,
    _test_single_id_async,
    _test_single_id_with_baselines,
    _test_single_id_with_baselines_async,
)
from .detector import detect_idor_flaws, detect_idor_flaws_async

# Enhanced access detection capabilities
from .enhanced_detector import (
    EnhancedAccessTestConfig,
    EnhancedAccessTester,
    EnhancedAccessTestResults,
    create_enhanced_access_config,
    privilege_escalation_test_only,
    quick_idor_with_smart_ids,
    run_enhanced_access_detection,
    run_enhanced_access_detection_sync,
    tenant_isolation_test_only,
)

# ID Generation and Fuzzing
from .id_generation import (
    EnhancedIDGenerator,
    IDGenerationConfig,
    IDPattern,
    IDType,
    PatternDetector,
    create_id_generation_config,
    generate_smart_id_list,
)

# Logging functions are imported from logicpwn.core.logging in individual modules
from .models import AccessDetectorConfig, AccessTestResult

# Privilege Escalation and Role Testing
from .privilege_escalation import (
    PermissionType,
    PrivilegeEscalationTester,
    PrivilegeLevel,
    PrivilegeTestResult,
    RoleDefinition,
    RoleHierarchyMapper,
    RoleTestConfig,
    RoleTestType,
    create_role_test_config,
    run_comprehensive_privilege_escalation_test,
)

# Tenant Isolation Testing
from .tenant_isolation import (
    TenantContext,
    TenantEnumerator,
    TenantIsolationLevel,
    TenantIsolationTester,
    TenantTestConfig,
    TenantTestResult,
    TenantTestType,
    create_tenant_test_config,
    run_comprehensive_tenant_isolation_test,
)
from .validation import _sanitize_test_id, _validate_endpoint_template, _validate_inputs
