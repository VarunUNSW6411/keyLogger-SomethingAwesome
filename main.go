package main

import (
	"encoding/json"
	"github.com/alexflint/go-arg"
	"gopkg.in/yaml.v3"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"fmt"
)

type SendCmd struct {
	Path string `arg:"positional"`
}

var args struct {
	Send    *SendCmd `arg:"subcommand:send" help:"can also use -d to provide the path to file"`
}

type content struct {
	DataJSON []byte `json:"result"`
}

func isJSON(s string) bool {
	var js map[string]interface{}
	return json.Unmarshal([]byte(s), &js) == nil
}

func isYAML(s string) bool {
	var js map[string]interface{}
	return yaml.Unmarshal([]byte(s), &js) == nil
}

func sendRequest(requestBody []byte, url string, contentType string) {
	con := strings.NewReader(string(requestBody))
	req, err := http.NewRequest("POST", url, con)
	if err != nil {
		panic(err)
	}
	req.Header.Set("Content-Type", contentType)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println(body)

}

func main() {
	arg.MustParse(&args)


	switch {
	case args.Send != nil && args.Send.Path != "":
		fmt.Println("Getting file from location %s\n", args.Send.Path)

		data, err := os.Open(args.Send.Path)
		if err != nil {
			fmt.Println("Error", err)
		}
		fileData, _ := ioutil.ReadAll(data)

		url := "https://c6ltyrte3d.execute-api.ap-southeast-2.amazonaws.com/api/openapi"

		var readFileContent []byte
		var requestBody []byte
		readFileContent, _ = ioutil.ReadFile(args.Send.Path)

		if isJSON(string(fileData)) || isYAML(string(fileData)) {
			requestPayload := content{DataJSON: readFileContent}
			requestBody, _ = json.Marshal(requestPayload)
			sendRequest(requestBody, url, "application/json")
		} else {
			fmt.Println("Please provide either a JSON or YAML file")
		}

	default:
		p := arg.MustParse(&args)
		p.WriteHelp(os.Stdout)
	}
}
