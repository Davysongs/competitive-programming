// Problem: Lexicographic Rank Sum Queries
// Approach: Compact suffix automaton with lexicographic subtree counts.
// Time: O((|s| + total query length) * alphabet size).
// Space: O(|s| * alphabet size).
package main

import (
	"encoding/json"
	"fmt"
	"os"
)

const modulus int64 = 1_000_000_007

type input struct {
	Source  string   `json:"s"`
	Queries []string `json:"queries"`
}

type state struct {
	next    [26]int32
	link    int32
	longest int32
}

type suffixAutomaton struct {
	states []state
	last   int32
}

func newSuffixAutomaton(capacity int) *suffixAutomaton {
	states := make([]state, 1, capacity)
	states[0].link = -1
	return &suffixAutomaton{states: states}
}

func (automaton *suffixAutomaton) extend(character byte) {
	edge := character - 'a'
	current := int32(len(automaton.states))
	automaton.states = append(automaton.states, state{
		link:    -1,
		longest: automaton.states[automaton.last].longest + 1,
	})

	parent := automaton.last
	for parent != -1 && automaton.states[parent].next[edge] == 0 {
		automaton.states[parent].next[edge] = current
		parent = automaton.states[parent].link
	}

	if parent == -1 {
		automaton.states[current].link = 0
	} else {
		successor := automaton.states[parent].next[edge]
		if automaton.states[parent].longest+1 == automaton.states[successor].longest {
			automaton.states[current].link = successor
		} else {
			clone := int32(len(automaton.states))
			cloneState := automaton.states[successor]
			cloneState.longest = automaton.states[parent].longest + 1
			automaton.states = append(automaton.states, cloneState)

			for parent != -1 && automaton.states[parent].next[edge] == successor {
				automaton.states[parent].next[edge] = clone
				parent = automaton.states[parent].link
			}
			automaton.states[successor].link = clone
			automaton.states[current].link = clone
		}
	}

	automaton.last = current
}

func buildSuffixAutomaton(text string) *suffixAutomaton {
	automaton := newSuffixAutomaton(2*len(text) + 1)
	for index := 0; index < len(text); index++ {
		automaton.extend(text[index])
	}
	return automaton
}

func (automaton *suffixAutomaton) reachableCounts(maximumLength int) []int64 {
	lengthCounts := make([]int, maximumLength+1)
	for index := range automaton.states {
		lengthCounts[automaton.states[index].longest]++
	}
	for length := 1; length <= maximumLength; length++ {
		lengthCounts[length] += lengthCounts[length-1]
	}

	order := make([]int32, len(automaton.states))
	for index := len(automaton.states) - 1; index >= 0; index-- {
		length := automaton.states[index].longest
		lengthCounts[length]--
		order[lengthCounts[length]] = int32(index)
	}

	reachable := make([]int64, len(automaton.states))
	for orderIndex := len(order) - 1; orderIndex >= 0; orderIndex-- {
		stateIndex := order[orderIndex]
		for _, nextState := range automaton.states[stateIndex].next {
			if nextState != 0 {
				reachable[stateIndex] += 1 + reachable[nextState]
			}
		}
	}
	return reachable
}

func triangularModulo(value int64) int64 {
	if value%2 == 0 {
		return ((value / 2) % modulus) * ((value + 1) % modulus) % modulus
	}
	return (value % modulus) * (((value + 1) / 2) % modulus) % modulus
}

func solve(data input) [][2]int64 {
	automaton := buildSuffixAutomaton(data.Source)
	reachable := automaton.reachableCounts(len(data.Source))
	answers := make([][2]int64, 0, len(data.Queries))

	for _, query := range data.Queries {
		var count int64
		var rankSum int64
		var rankOffset int64
		var stateIndex int32

		for characterIndex := 0; characterIndex < len(query); characterIndex++ {
			edge := query[characterIndex] - 'a'
			for smallerEdge := byte(0); smallerEdge < edge; smallerEdge++ {
				nextState := automaton.states[stateIndex].next[smallerEdge]
				if nextState == 0 {
					continue
				}
				blockSize := 1 + reachable[nextState]
				rankSum += (blockSize % modulus) * (rankOffset % modulus)
				rankSum += triangularModulo(blockSize)
				rankSum %= modulus
				count += blockSize
				rankOffset += blockSize
			}

			nextState := automaton.states[stateIndex].next[edge]
			if nextState == 0 {
				break
			}
			stateIndex = nextState
			count++
			rankOffset++
			rankSum = (rankSum + rankOffset) % modulus
		}

		answers = append(answers, [2]int64{count, rankSum})
	}
	return answers
}

func main() {
	var data input
	if err := json.NewDecoder(os.Stdin).Decode(&data); err != nil {
		fmt.Fprintln(os.Stderr, "invalid JSON input:", err)
		os.Exit(1)
	}
	if err := json.NewEncoder(os.Stdout).Encode(solve(data)); err != nil {
		fmt.Fprintln(os.Stderr, "failed to encode result:", err)
		os.Exit(1)
	}
}
