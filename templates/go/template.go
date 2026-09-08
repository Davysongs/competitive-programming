// Minimal Go competitive-programming template.
package main

import (
	"bufio"
	"os"
)

func solve(in *bufio.Reader, out *bufio.Writer) {
	// Parse the problem-specific input and write the answer.
}

func main() {
	in := bufio.NewReader(os.Stdin)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()
	solve(in, out)
}
