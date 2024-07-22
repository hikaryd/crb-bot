import os
import re
import site

aioredis_path = os.path.join(site.getsitepackages()[0], "aioredis", "exceptions.py")

with open(aioredis_path, "r") as f:
    content = f.read()

pattern = (
    r"class TimeoutError\(asyncio\.TimeoutError, builtins\.TimeoutError, RedisError\):"
)
replacement = "class TimeoutError(RedisError):"

patched_content = re.sub(pattern, replacement, content)

with open(aioredis_path, "w") as f:
    f.write(patched_content)
