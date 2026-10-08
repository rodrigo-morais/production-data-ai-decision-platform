package main

import "testing"

func TestScore(t *testing.T) {
	got := score(request{Impact: 0.8, Urgency: 0.6, Coverage: 1.0})
	if got < 0.76 || got > 0.78 {
		t.Fatalf("unexpected score: %f", got)
	}
}

func TestClamp(t *testing.T) {
	if clamp(-1) != 0 || clamp(2) != 1 {
		t.Fatal("clamp did not enforce bounds")
	}
}

func BenchmarkScore(b *testing.B) {
	input := request{Impact: 0.8, Urgency: 0.6, Coverage: 1.0}
	for range b.N {
		_ = score(input)
	}
}
