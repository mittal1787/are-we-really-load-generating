package main

import (
	"flag"
	"time"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"os"
)

func main() {
	wwwDir := flag.String("www", "www", "directory with files to be served")
	wwwPort := flag.Int("port", 8001, "http port")

	flag.Parse()

	log.Printf("Serving files from '%s'", *wwwDir)

	http.HandleFunc("/", handler)

	log.Printf("Starting HTTP server on port %d", *wwwPort)
	err := http.ListenAndServe(":"+strconv.Itoa(*wwwPort), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(time.Now().UnixNano())
	duration, err := time.ParseDuration(os.Args[1])
	if err == nil {
		fmt.Printf(os.Stderr, os.Args[1])
		time.Sleep(duration)
	} else {
		fmt.Printf(os.Stderr, err)
	}
	fmt.Fprint(w, "Hello !")
}
