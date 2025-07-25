use ic_cdk::query;
use ic_http_outcalls::{make_http_request, HttpRequest, HttpMethod};

#[query]
async fn fetch_page(url: String) -> String {
    let request = HttpRequest {
        url,
        method: HttpMethod::GET,
        headers: vec![],
        body: None,
        max_response_bytes: Some(2_000_000),
    };

    match make_http_request(request).await {
        Ok(response) => String::from_utf8_lossy(&response.body).to_string(),
        Err(e) => format!("Error: {}", e),
    }
}
