def verify_env_inputs(num_documento_princ: str, login_password: str, guest_numdoc: str) -> None:
    """Verify that required inputs are not empty strings."""
    missing_vars = []
    if not num_documento_princ:
        missing_vars.append("NUM_DOCUMENTO_PRINC")
    if not login_password:
        missing_vars.append("LOGIN_PASSWORD")
    if not guest_numdoc:
        missing_vars.append("GUEST_NUMDOC")

    if missing_vars:
        raise ValueError(f"The following required environment variables are missing or empty: {', '.join(missing_vars)}")