package main

import (
    "fmt"
    "io/ioutil"
	"encoding/json"
    "net/http"
	"time"
	"math"
	// "bytes"
)

type Response struct {
	Data []struct {
		TraceID string `json:"traceID"`
		Spans   []struct {
			TraceID       string `json:"traceID"`
			SpanID        string `json:"spanID"`
			Flags         int    `json:"flags"`
			OperationName string `json:"operationName"`
			References    []struct {
				RefType string `json:"refType"`
				TraceID string `json:"traceID"`
				SpanID  string `json:"spanID"`
			} `json:"references"`
			StartTime int64 `json:"startTime"`
			Duration  int   `json:"duration"`
			Tags      interface{} `json:"tags"`
			Logs      []any  `json:"logs"`
			ProcessID string `json:"processID"`
			Warnings  any    `json:"warnings"`
		} `json:"spans"`
		Processes struct {
			P1 struct {
				ServiceName string `json:"serviceName"`
				Tags        []struct {
					Key   string `json:"key"`
					Type  string `json:"type"`
					Value string `json:"value"`
				} `json:"tags"`
			} `json:"p1"`
			P2 struct {
				ServiceName string `json:"serviceName"`
				Tags        []struct {
					Key   string `json:"key"`
					Type  string `json:"type"`
					Value string `json:"value"`
				} `json:"tags"`
			} `json:"p2"`
			P3 struct {
				ServiceName string `json:"serviceName"`
				Tags        []struct {
					Key   string `json:"key"`
					Type  string `json:"type"`
					Value string `json:"value"`
				} `json:"tags"`
			} `json:"p3"`
			P4 struct {
				ServiceName string `json:"serviceName"`
				Tags        []struct {
					Key   string `json:"key"`
					Type  string `json:"type"`
					Value string `json:"value"`
				} `json:"tags"`
			} `json:"p4"`
			P5 struct {
				ServiceName string `json:"serviceName"`
				Tags        []struct {
					Key   string `json:"key"`
					Type  string `json:"type"`
					Value string `json:"value"`
				} `json:"tags"`
			} `json:"p5"`
			P6 struct {
				ServiceName string `json:"serviceName"`
				Tags       interface{} `json:"tags"`
			} `json:"p6"`
		} `json:"processes"`
		Warnings any `json:"warnings"`
	} `json:"data"`
	Total  int `json:"total"`
	Limit  int `json:"limit"`
	Offset int `json:"offset"`
	Errors any `json:"errors"`
}

type DataPoint struct {
	duration int
	timestamp int
}

type ResponseToSend struct {
	Data []DataPoint
}

var myClient = &http.Client{Timeout: 10 * time.Minute}


func parse_traces(w http.ResponseWriter, req *http.Request) {
	fmt.Println("Get client data")
	r, err := myClient.Get("http://localhost:16686/api/traces?service=search&lookback=30s&limit=300000")
    if err != nil {
		fmt.Println(err)
		return
    }
    defer r.Body.Close()
	var result Response
	fmt.Println("Got client data")
    body, err := ioutil.ReadAll(r.Body) // response body is []byte
	// fmt.Println(string(body)) 
	if err := json.Unmarshal(body, &result); err != nil {   // Parse []byte to go struct pointer
		fmt.Println(err)
		fmt.Println("Can not unmarshal JSON")
		return
	}

	var finalResponse ResponseToSend 
	finalResponse.Data = nil

	// var buffer bytes.Buffer

	// buffer.WriteString("Start time,Duration\n")
    // fmt.Println(buffer.String())
	w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusCreated)
	fmt.Fprintf(w,"Start time,Duration\n")
	for _, trace := range result.Data {
		var startTime = math.Inf(1)
		var endTime = math.Inf(-1)
		for _, span := range trace.Spans {
			startTime = math.Min(startTime, float64(span.StartTime))
			endTime = math.Max(endTime, float64(int(span.StartTime) + span.Duration))
		}
		fmt.Fprintf(w, "%f,%f\n", startTime, endTime - startTime)
	}
	fmt.Println("Finish parsing file")
}

func main() {
	
	http.HandleFunc("/hello", parse_traces)
	http.ListenAndServe(":8000", nil)
	// foo1 := new(Foo) // or &Foo{}
	// getJson("http://clnode028.clemson.cloudlab.us:16686/api/traces?service=search&lookback=30s&prettyPrint=true&limit=100", foo1)
	// fmt.Println(foo1.Bar)

	// // alternately:

	// foo2 := Foo{}
	// getJson("http://example.com", &foo2)
	// fmt.Println(foo2.Bar)
	// resp, err := http.Get("http://clnode028.clemson.cloudlab.us:16686/api/traces?service=search&lookback=5m&prettyPrint=true&limit=1")
    // if err != nil {
    //     fmt.Println("No response from request")
    // }
    // defer resp.Body.Close()
    // body, err := ioutil.ReadAll(resp.Body) // response body is []byte
    // var result Response
	// if err := json.Unmarshal(body, &result); err != nil {   // Parse []byte to go struct pointer
	// 	fmt.Println("Can not unmarshal JSON")
	// }
	// fmt.Println(PrettyPrint(result))
}
	