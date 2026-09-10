// Problem: Data Stream Transmission
// Approach: Exchange-argument ordering followed by sequence partition DP.
// Time: O(n log n + k * n^2).
// Space: O(n).
package main

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"sort"
)

type input struct {
	PacketCount     int          `json:"n"`
	CheckpointCount int          `json:"k"`
	Packets         [][2]float64 `json:"packets"`
}

type packet struct {
	duration           float64
	successProbability float64
}

func orderingKey(value packet) float64 {
	failureProbability := 1 - value.successProbability
	if failureProbability == 0 {
		return math.Inf(1)
	}
	return value.duration / failureProbability
}

func roundToSix(value float64) float64 {
	return math.RoundToEven(value*1_000_000) / 1_000_000
}

func solve(data input) float64 {
	packets := make([]packet, data.PacketCount)
	for index, values := range data.Packets {
		packets[index] = packet{
			duration:           values[0],
			successProbability: values[1],
		}
	}
	sort.SliceStable(packets, func(left, right int) bool {
		return orderingKey(packets[left]) < orderingKey(packets[right])
	})

	successPrefix := make([]float64, data.PacketCount+1)
	weightedDurationPrefix := make([]float64, data.PacketCount+1)
	successPrefix[0] = 1
	for index, value := range packets {
		successPrefix[index+1] = successPrefix[index] * value.successProbability
		weightedDurationPrefix[index+1] = weightedDurationPrefix[index] +
			value.duration*successPrefix[index]
	}

	segmentCost := func(start, end int) float64 {
		return (weightedDurationPrefix[end+1] - weightedDurationPrefix[start]) /
			successPrefix[end+1]
	}

	costs := make([]float64, data.PacketCount)
	for end := range costs {
		costs[end] = segmentCost(0, end)
	}
	answer := costs[data.PacketCount-1]
	maximumSegments := min(data.CheckpointCount+1, data.PacketCount)

	for segmentCount := 2; segmentCount <= maximumSegments; segmentCount++ {
		nextCosts := make([]float64, data.PacketCount)
		for index := range nextCosts {
			nextCosts[index] = math.Inf(1)
		}
		for end := segmentCount - 1; end < data.PacketCount; end++ {
			inverseSuccess := 1 / successPrefix[end+1]
			best := math.Inf(1)
			for split := segmentCount - 2; split < end; split++ {
				candidate := costs[split] +
					(weightedDurationPrefix[end+1]-weightedDurationPrefix[split+1])*
						inverseSuccess
				best = math.Min(best, candidate)
			}
			nextCosts[end] = best
		}
		costs = nextCosts
		answer = math.Min(answer, costs[data.PacketCount-1])
	}

	return roundToSix(answer)
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
