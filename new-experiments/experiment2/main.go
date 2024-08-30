package main

import (
	"flag"
	"time"
	"fmt"
	"log"
	"net/http"
	"strconv"
)

func main() {
	wwwDir := flag.String("www", "www", "directory with files to be served")
	wwwPort := flag.Int("port", 8000, "http port")

	flag.Parse()

	log.Printf("Serving files from '%s'", *wwwDir)

	http.HandleFunc("/hello", handler)
	http.Handle("/", http.StripPrefix("/", http.FileServer(http.Dir(*wwwDir))))

	log.Printf("Starting HTTP server on port %d", *wwwPort)
	err := http.ListenAndServe(":"+strconv.Itoa(*wwwPort), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(time.Now().UnixNano())
	sum := 1
	for i := 1; i < 100000; i++ {
		for j := 1; j < 100000; j++ {
			sum *= i*j
		}
	}
	fmt.Fprint(w, "Hello !")
}
