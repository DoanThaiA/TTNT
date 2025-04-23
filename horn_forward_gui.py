import re

def parse_rule_mixed(expr):
    """
    Phân tích 2 dạng nhập từ bàn phím:
    - Logic: ~A | ~B | C  (thay cho ¬A ∨ ¬B ∨ C)
    - Luật:  A ^ B => C
    """
    expr = expr.strip()
    if '=>' in expr:
        parts = expr.split('=>')
        premises = set(p.strip() for p in parts[0].split('^'))
        conclusion = parts[1].strip()
        return (premises, conclusion)
    elif '|' in expr:
        literals = [x.strip() for x in expr.split('|')]
        negative = set()
        positive = None
        for lit in literals:
            if lit.startswith('~'):
                negative.add(lit[1:].strip())
            else:
                if positive is not None:
                    raise ValueError("Không phải mệnh đề Horn: nhiều literal dương")
                positive = lit
        if positive:
            return (negative, positive)
        else:
            raise ValueError("Không có literal dương, không phải luật Horn")
    else:
        return (set(), expr.strip())

def forward_chaining_with_trace(rules, facts):
    known = set(facts)
    inferred = set()
    trace = {}
    new_fact = True

    while new_fact:
        new_fact = False
        for premises, conclusion in rules:
            if premises.issubset(known) and conclusion not in known:
                known.add(conclusion)
                inferred.add(conclusion)
                trace[conclusion] = (premises, conclusion)
                new_fact = True
    return inferred.union(facts), trace

def detect_redundant_rules(rules, facts):
    redundant = []
    full_inference, _ = forward_chaining_with_trace(rules, facts)
    for i, rule in enumerate(rules):
        test_rules = rules[:i] + rules[i+1:]
        result, _ = forward_chaining_with_trace(test_rules, facts)
        if result == full_inference:
            redundant.append(rule)
    return redundant

# ================================
# Nhập dữ liệu từ người dùng
# ================================

print("Nhập các mệnh đề logic (ví dụ: ~A | ~B | C hoặc A ^ B => C). Nhập 'done' để kết thúc:")
user_rules = []
while True:
    line = input("Mệnh đề: ")
    if line.lower() == 'done':
        break
    try:
        rule = parse_rule_mixed(line)
        user_rules.append(rule)
    except Exception as e:
        print(f" Lỗi: {e}")

initial_facts = input("Nhập các sự thật ban đầu (vd: A,B): ")
facts = set(x.strip() for x in initial_facts.split(','))

# ================================
# Hiển thị các luật Horn
# ================================

print("\n Các luật Horn đã chuyển:")
for premises, conclusion in user_rules:
    if premises:
        print(f"{' ^ '.join(sorted(premises))} => {conclusion}")
    else:
        print(f"{conclusion} (fact)")

# ================================
# 🔍 Suy diễn & phát hiện luật dư
# ================================

inferred_facts, trace = forward_chaining_with_trace(user_rules, facts)
redundant = detect_redundant_rules(user_rules, facts)

print("\n Suy diễn được các sự thật:")
print(", ".join(sorted(inferred_facts)))

print("\n Chi tiết suy diễn:")
for conclusion, (premises, _) in trace.items():
    if premises:
        print(f"{' ^ '.join(sorted(premises))} => {conclusion}")
    else:
        print(f"{conclusion} là sự thật ban đầu")

print("\n Các luật dư thừa là:")
for premises, conclusion in redundant:
    if premises:
        print(f"{' ^ '.join(sorted(premises))} => {conclusion}")
    else:
        print(f"{conclusion} (fact)")
