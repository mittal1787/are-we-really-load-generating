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
	wwwPort := flag.Int("port", 8001, "http port")

	flag.Parse()

	http.HandleFunc("/", handler)

	log.Printf("Starting HTTP server on port %d", *wwwPort)
	err := http.ListenAndServe(":"+strconv.Itoa(*wwwPort), nil)
	if err != nil {
		log.Fatal(err.Error())
	}
}

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println(time.Now().UnixNano())
	fmt.Fprint(w, "Hello !")
}
