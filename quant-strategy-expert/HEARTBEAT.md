# HEARTBEAT.md

_本 Agent 默认不需要心跳轮询。回测任务都是用户主动发起的,没有需要定时检查的项。_

_如果未来要加(例如每日盘后跑某只标的的 sanity check),在下面追加任务,保持极简。_

```markdown
# 默认空。Agent 收到 heartbeat 直接回 HEARTBEAT_OK。
```
