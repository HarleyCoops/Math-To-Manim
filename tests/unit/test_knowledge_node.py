"""Unit tests for KnowledgeNode data structure."""

import pytest

from src.agents.knowledge_node import KnowledgeNode


class TestKnowledgeNode:
    """Tests for KnowledgeNode creation and serialization."""

    def test_create_foundation_node(self):
        node = KnowledgeNode(concept="velocity", depth=2, is_foundation=True)
        assert node.concept == "velocity"
        assert node.depth == 2
        assert node.is_foundation is True
        assert node.prerequisites == []
        assert node.equations is None

    def test_create_node_with_prerequisites(self):
        child = KnowledgeNode(concept="velocity", depth=1, is_foundation=True)
        parent = KnowledgeNode(
            concept="momentum",
            depth=0,
            is_foundation=False,
            prerequisites=[child],
        )
        assert len(parent.prerequisites) == 1
        assert parent.prerequisites[0].concept == "velocity"

    def test_to_dict(self):
        child = KnowledgeNode(concept="velocity", depth=1, is_foundation=True)
        parent = KnowledgeNode(
            concept="momentum",
            depth=0,
            is_foundation=False,
            prerequisites=[child],
            equations=[r"$p = mv$"],
            definitions={"p": "momentum", "m": "mass", "v": "velocity"},
        )
        d = parent.to_dict()
        assert d["concept"] == "momentum"
        assert d["is_foundation"] is False
        assert len(d["prerequisites"]) == 1
        assert d["prerequisites"][0]["concept"] == "velocity"
        assert d["equations"] == [r"$p = mv$"]
        assert d["definitions"]["p"] == "momentum"

    def test_from_dict_roundtrip(self):
        original = KnowledgeNode(
            concept="QFT",
            depth=0,
            is_foundation=False,
            prerequisites=[
                KnowledgeNode(concept="quantum mechanics", depth=1, is_foundation=False,
                              prerequisites=[
                                  KnowledgeNode(concept="linear algebra", depth=2, is_foundation=True),
                              ]),
                KnowledgeNode(concept="special relativity", depth=1, is_foundation=True),
            ],
        )
        d = original.to_dict()
        restored = KnowledgeNode.from_dict(d)
        assert restored.concept == "QFT"
        assert len(restored.prerequisites) == 2
        assert restored.prerequisites[0].prerequisites[0].concept == "linear algebra"

    def test_node_count(self):
        tree = KnowledgeNode(
            concept="A", depth=0, is_foundation=False,
            prerequisites=[
                KnowledgeNode(concept="B", depth=1, is_foundation=True),
                KnowledgeNode(concept="C", depth=1, is_foundation=False,
                              prerequisites=[
                                  KnowledgeNode(concept="D", depth=2, is_foundation=True),
                              ]),
            ],
        )
        assert tree.node_count() == 4

    def test_flatten(self):
        tree = KnowledgeNode(
            concept="A", depth=0, is_foundation=False,
            prerequisites=[
                KnowledgeNode(concept="B", depth=1, is_foundation=True),
                KnowledgeNode(concept="C", depth=1, is_foundation=True),
            ],
        )
        flat = tree.flatten()
        concepts = [n.concept for n in flat]
        assert concepts == ["A", "B", "C"]

    def test_print_tree(self, capsys):
        tree = KnowledgeNode(
            concept="momentum", depth=0, is_foundation=False,
            prerequisites=[
                KnowledgeNode(concept="velocity", depth=1, is_foundation=True),
            ],
        )
        tree.print_tree()
        output = capsys.readouterr().out
        assert "momentum" in output
        assert "velocity" in output
        assert "FOUNDATION" in output
