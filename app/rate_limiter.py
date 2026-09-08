from fastapi import Request, HTTPException
from app.redis_client import redis_client
import math

TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])

local time_result = redis.call('TIME')
local now = tonumber(time_result[1]) * 1000 +
            math.floor(tonumber(time_result[2]) / 1000)

local tokens = tonumber(redis.call('HGET', key, 'tokens'))
local last_refill = tonumber(redis.call('HGET', key, 'last_refill'))

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = (now - last_refill) / 1000

tokens = math.min(
    capacity,
    tokens + (elapsed * refill_rate)
)

local allowed = 0

if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call('HSET', key, 'tokens', tokens)
redis.call('HSET', key, 'last_refill', now)

local ttl = math.ceil(capacity / refill_rate) + 1
redis.call('EXPIRE', key, ttl)

return {allowed, tokens}
"""
def rate_limit(request: Request):

    ip = request.client.host

    key = f"token_bucket:{ip}"
    capacity=10
    refill_rate=10/60

    result=redis_client.eval(TOKEN_BUCKET_SCRIPT,1,key,capacity,refill_rate)
    allowed=result[0]
    tokens =float(result[1])

    if allowed==0:
        retry_after = math.ceil((1 - tokens) / refill_rate)
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Try again in {retry_after} seconds."
        )