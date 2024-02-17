use std::{fs::File, time::Duration};

use actix_web::{middleware, rt::time, web, App, HttpServer};

use clap::Parser;
use log::LevelFilter;

/// Fast HTTP mock server
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// port to listen on
    #[arg(short, long)]
    port: u16,

    /// request processing delay in milliseconds
    #[arg(short, long, default_value_t = 0)]
    delay: u64,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
    let target = Box::new(File::create("log.txt").expect("Can't create file"));

    env_logger::Builder::new()
        .target(env_logger::Target::Pipe(target))
        .filter(Some("arrival_time"), LevelFilter::Info)
        .init();

    let args = Args::parse();

    log::info!("starting HTTP server at http://localhost:{}", args.port);

    HttpServer::new(move || {
        App::new()
            .wrap(middleware::Logger::new("%r %s %b %t %Dms").log_target("arrival_time"))
            .service(web::resource("/").to(move || async move {
                time::sleep(Duration::from_millis(args.delay)).await;
                "Success!"
            }))
    })
    .bind_auto_h2c(("127.0.0.1", args.port))?
    .run()
    .await
}
