# Example Input

**User Request**: "Explain the Pythagorean theorem with a visual proof"

## Agent 1: ConceptAnalyzer Output

```json
{
  "core_concept": "Pythagorean theorem",
  "domain": "mathematics/geometry",
  "level": "beginner",
  "goal": "Understand and visualize the relationship between sides of a right triangle"
}
```

## Agent 2: PrerequisiteExplorer Output

### Knowledge Tree Structure

```
Pythagorean theorem (depth 0)
├─ right triangle (depth 1)
│   ├─ angles (depth 2) [FOUNDATION]
│   └─ sides of a triangle (depth 2) [FOUNDATION]
├─ squares and area (depth 1)
│   └─ multiplication (depth 2) [FOUNDATION]
└─ equality (depth 1) [FOUNDATION]
```

### Topological Order (Foundation -> Target)

1. angles
2. sides of a triangle
3. right triangle
4. multiplication
5. squares and area
6. equality
7. Pythagorean theorem
