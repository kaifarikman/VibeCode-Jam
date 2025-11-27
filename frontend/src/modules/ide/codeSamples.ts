export const codeSamples: Record<string, string> = {
  python: `def main():
    pass


if __name__ == "__main__":
    main()
`,
  typescript: `function main(): void {
  // Your code here
}

main();
`,
  go: `package main

import "fmt"

func main() {
  // Your code here
}
`,
  java: `public class Solution {
    public static void main(String[] args) {
        // Your code here
    }
}
`,
}

export const getSolutionFileName = (language: string): string => {
  const extMap: Record<string, string> = {
    python: 'solution.py',
    typescript: 'solution.ts',
    go: 'solution.go',
    java: 'Solution.java',
  }
  return extMap[language] || 'solution.py'
}

export const getLanguageFromFileName = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase()
  const extMap: Record<string, string> = {
    py: 'python',
    ts: 'typescript',
    go: 'go',
    java: 'java',
  }
  return extMap[ext || ''] || 'python'
}

