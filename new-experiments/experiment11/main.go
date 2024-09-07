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
	wwwPort := flag.Int("port", 8000, "http port")

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
	duration, err = strconv.Atoi(os.Args[1])
	if err == nil {
		time.Sleep(duration * time.Second)
	}
	fmt.Fprint(w, "Hello !")
}
