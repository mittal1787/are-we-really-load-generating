use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use clap::Parser;
use reqwest::Url;
use tokio::{select, time};

/// Simple Load Generator
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// URL of the endpoint
    #[arg(short, long)]
    endpoint: Url,

    /// number of request per second
    #[arg(short, long, default_value_t = 1.0)]
    rps: f64,

    /// Duration of testing in seconds
    #[arg(short, long, default_value_t = 60.0)]
    test_duration: f64,
}

// #[tokio::main]
#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), reqwest::Error> {
    let args = Args::parse();

    let period_microsec = Arc::from((1_000_000.0 / args.rps).round() as u64);
    let test_duration = Duration::from_secs_f64(args.test_duration);

    let start_time = Instant::now();
    let mut interval = time::interval(Duration::from_micros(*period_microsec));

    let mut req_id = 0;
    while start_time.elapsed() < test_duration {
        select! {
            _ = interval.tick() => {
                tokio::spawn(make_request(args.endpoint.clone().into(), req_id));
            }
        }
        req_id += 1;
    }

    Ok(())
}

async fn make_request(endpoint: Arc<Url>, request_id: usize) {
    let url: Url = Arc::<reqwest::Url>::into_inner(endpoint).unwrap();
    let start_time = SystemTime::now();
    println!(
        "S, {}, {}",
        request_id,
        start_time
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_micros()
    );
    match reqwest::get(url).await {
        Ok(_res) => {
            let end_time = SystemTime::now();
            let response_time = end_time.duration_since(start_time).unwrap();
            println!(
                "R, {}, {}, {}",
                request_id,
                end_time
                    .duration_since(UNIX_EPOCH)
                    .expect("Time went backwards")
                    .as_micros(),
                response_time.as_micros()
            );
            // println!("Status: {}", res.status());
            // println!("Headers:\n{:#?}", res.headers());
        }
        Err(err) => {
            println!("E, {}, {}", request_id, err)
        }
    }
}
