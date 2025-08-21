use ic_cdk::update;
use ic_cdk::api::management_canister::http_request::{
    http_request, CanisterHttpRequestArgument, HttpMethod, HttpHeader,
};
use candid::{CandidType, Deserialize, Nat};
use serde::Serialize;

#[derive(CandidType, Deserialize, Serialize, Debug, Clone)]
pub struct PageResult {
    pub status: Nat,
    pub headers: Vec<HttpHeader>,
    pub body: String,
}

#[update]
async fn fetch_page(url: String) -> PageResult {
    let request = CanisterHttpRequestArgument {
        url,
        method: HttpMethod::GET,
        headers: vec![],
        body: None,
        max_response_bytes: Some(2_000_000), // 2MB limit
        transform: None,
    };

    // cycles required for http_request (tweak based on payload size)
    let cycles: u128 = 30_000_000_000;

    match http_request(request, cycles).await {
        Ok((response,)) => PageResult {
            status: Nat::from(response.status),
            headers: response.headers,
            body: String::from_utf8_lossy(&response.body).to_string(),
        },
        Err((code, msg)) => PageResult {
            status: Nat::from(500u16),
            headers: vec![HttpHeader {
                name: "IC-Error".to_string(),
                value: format!("{:?}", code),
            }],
            body: format!("error: {:?}", msg),
        },
    }
}
