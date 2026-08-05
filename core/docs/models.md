# SearchSession

## initialize(url)

The `initialize` method in SearchSession is responsible for:

1. Performing the initial GET request to the server using `HttpClient.get(url)`
2. Receiving the HTML response
3. Parsing the HTML to extract hidden PRADO fields:
   - `prado_page_state`
   - `prado_postback_target`
   - `prado_postback_parameter`
4. Storing these values in `self.state` for use in future requests
5. Wrapping any parsing errors in `SessionInitializationError`

This is a one-time setup that establishes a valid session with the server.

## get(url)

The `get` method performs subsequent requests during an active session:

1. Sends a GET request via `HttpClient.get(url)`
2. Automatically refreshes PRADO state from the response HTML
3. Returns the response for further processing

Unlike `initialize`, it doesn't wrap parsing errors in initialization-specific exceptions. 