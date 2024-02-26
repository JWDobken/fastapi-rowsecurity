Always = "true"
Never = "false"

# ID principals
Authenticated = "current_setting('app.current_user_id')::INTEGER IS NOT NULL"
UserOwner = "owner_id = current_setting('app.current_user_id')::integer"

# UUID principals
UserOwnerUuid = "owner_id = current_setting('app.current_user_id')::UUID"
