# HttpClient

## get(url, **kwargs)

The `get` method is a simple wrapper that:

1. Takes a URL path or full URL
2. Calls the internal `_request` method with `method="GET"`
3. Returns the raw HTTP response

## post(url, **kwargs)

The `post` method performs POST requests:

1. Takes a URL path or full URL
2. Calls the internal `_request` method with `method="POST"`
3. Returns the raw HTTP response

## _request(method, url, **kwargs)

The `_request` method handles the actual HTTP communication:

1. Builds the full URL using `_build_url()`
2. Sends the request with:
   - Automatic timeout (from kwargs or default)
   - Redirect following enabled
   - Automatic retries on network failures (429, 500, 502, 503, 504)
   - Exponential backoff between retries
3. Raises `HttpRequestError` on any request failure
4. Returns the response on success

## Automatic Retries

The `_setup_retries` method (called in `__init__`):

- Configures retry logic with exponential backoff
- Retries on specific HTTP status codes (429, 500, 502, 503, 504)
- Allows up to 3 retries by default
- Waits 1s, 2s, 4s between attempts

This provides resilience against transient network failures and rate limiting.