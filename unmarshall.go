package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"text/template"
)

// TemplateData holds the dynamic values for the template.
type TemplateData struct {
	Prompt    string
	Steps     string
	ImagesCID string
}

// findLineAndChar finds the line and character position of the offset in the JSON string
func findLineAndChar(input string, offset int64) (line, char int) {
	lines := strings.Split(input, "\n")
	counter := 0

	for i, l := range lines {
		counter += len(l) + 1 // +1 for the newline character
		if counter >= int(offset) {
			return i + 1, int(offset) - (counter - len(l)) + 1
		}
	}

	return 1, int(offset)
}

// annotateErrorWithLine tries to find the line that causes the JSON unmarshal error
func annotateErrorWithLine(input string, err error) error {
	if syntaxErr, ok := err.(*json.SyntaxError); ok {
		line, char := findLineAndChar(input, syntaxErr.Offset)
		return fmt.Errorf("error in line %d, char %d: %v", line, char, err)
	}
	return err
}

// ValidateJSONTemplate opens a .json.tmpl file, processes the template, and validates its content as JSON
func ValidateJSONTemplate(filePath string, data TemplateData) (interface{}, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var lines []string
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}

	// Combine all lines into a single string
	completeTemplate := strings.Join(lines, "\n")

	// Create a new template and parse the input text.
	tmpl, err := template.New("jsonTemplate").Parse(completeTemplate)
	if err != nil {
		return nil, err
	}

	// Execute the template with the given data and capture the output.
	var processed bytes.Buffer
	if err := tmpl.Execute(&processed, data); err != nil {
		return nil, annotateErrorWithLine(completeTemplate, err)
	}

	fmt.Println("Processed template:", processed.String())

	// Unmarshal the processed template to validate JSON
	var jsonData interface{}
	if err := json.Unmarshal(processed.Bytes(), &jsonData); err != nil {
		// Enhanced error reporting
		return nil, annotateErrorWithLine(processed.String(), err)
	}

	return jsonData, nil
}

// Existing functions unchanged...

func main() {
	// Example data to pass into the template.
	data := TemplateData{
		Prompt:    "your-prompt",
		Steps:     "50",
		ImagesCID: "sdfsdfsd",
	}

	jsonData, err := ValidateJSONTemplate("/Users/arshath/play/lilypad/lilypad-module-test/lilypad_module.json.tmpl", data)
	if err != nil {
		fmt.Println("Error validating JSON template:", err)
		return
	}
	fmt.Println("JSON is valid:", jsonData)
}
