package main

import (
	"os"
	"fmt"
	"github.com/alexflint/go-arg"
)

type SendCmd struct {
	Path string `arg:"positional"`
}

var args struct {
	Send    *SendCmd `arg:"subcommand:send" help:"can also use -d to provide the path to file"`
	Verbose bool     `arg:"-v" help:"enable verbose logging"`
	Debug   bool     `arg:"-d" help:"enable debug logging"`
}

func main() {
	arg.MustParse(&args)

	// Configure logger


	switch {
	case args.Send != nil && args.Send.Path != "":
		fmt.Println("Getting file from location %s\n", args.Send.Path)


	default:
		p := arg.MustParse(&args)
		p.WriteHelp(os.Stdout)
	}
}
