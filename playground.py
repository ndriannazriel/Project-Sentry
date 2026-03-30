from litesoc import LiteSOC, SecurityEvents, Actor, EventSeverity

litesoc = LiteSOC(api_key="lsoc_live_fd18ae05944434159e3dea156a29b091", batching=True, batch_size=5, debug=True, silent=True)

# Single event
litesoc.track(SecurityEvents.AUTH_LOGIN_FAILED,
    actor_id="user_123",
    actor_email="user@example.com",
    user_ip="203.0.113.50",
    metadata={"reason":"invalid_password"}
)

# Batch example
events = [
    {"event_name":"auth.login_success","actor_id":"user_123","user_ip":"203.0.113.50"},
    {"event_name":"data.export","actor_id":"user_123","user_ip":"203.0.113.50","metadata":{"rows":10}},
]
accepted = litesoc.track_batch(events)
print("accepted:", accepted)

# Get alerts (may be plan-restricted)
try:
    alerts = litesoc.get_alerts(status="open", limit=10)
    print("alerts:", alerts.get("data", []) )
except Exception as e:
    print("alerts error:", e)

# Flush and shutdown
litesoc.flush()
litesoc.shutdown()