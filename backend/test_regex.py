import re

# 模拟流式 chunk
chunks = [
    "\n计算结果已经出来了，1+1=2。现在我可以回答用户的问题了。\n",
    "</think>\n\n",
]

# 测试我们的正则
for chunk in chunks:
    print(f"Chunk: {repr(chunk)}")
    thinking_matches = re.findall(r'<think>(.*?)</think>', chunk, re.DOTALL)
    print(f"  Thinking matches: {thinking_matches}")
    clean = re.sub(r'<think>.*?</think>', '', chunk, flags=re.DOTALL)
    print(f"  Clean: {repr(clean)}")
    print()

# 测试多行模式
chunk2 = "计算结果\n</think>\n\n完成"
print(f"Multi-line chunk: {repr(chunk2)}")
thinking_matches = re.findall(r'<think>(.*?)</think>', chunk2, re.DOTALL)
print(f"  Thinking matches: {thinking_matches}")