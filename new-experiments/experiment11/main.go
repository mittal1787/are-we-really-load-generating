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

var file, _ = os.OpenFile("machine.i.log", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)

func LogEvent(event string, rest ...any) {
	w := bufio.NewWriter(file)

	_, err := fmt.Fprintln(w, "[", time.Now().Unix(),"]",event, rest)
	if err != nil {
		panic(err)
	}

	// TODO: Use more efficient method later on writing to file immediately after logging
	w.Flush()
	file.Close()
	file, err = os.OpenFile("machine.i.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		panic(err)
	}
}


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
		LogEvent(os.Args[1])
		time.Sleep(duration)
	} else {
		LogEvent(err.Error())
	}
	fmt.Fprint(w, "Hello !")
}
