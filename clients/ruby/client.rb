require 'oauth'
require 'openssl'

# CONFIGURATION
# Target the Domain (Must match the cert CN)
SITE_URL = "https://127.0.0.1.nip.io:9090"

# Keys (Must match the Python Server exactly!)
CONSUMER_KEY    = "ClientKeyMustBeLongEnough00001"
CONSUMER_SECRET = "ClientSecretMustBeLongEnough01"

puts "--- RUBY CLIENT STARTING ---"
puts "Target: #{SITE_URL}"
puts "Key:    #{CONSUMER_KEY}"

# SETUP CONSUMER
# The :ssl option is critical here to bypass the "self-signed" error
consumer = OAuth::Consumer.new(CONSUMER_KEY, CONSUMER_SECRET, {
  :site               => SITE_URL,
  :scheme             => :header,        # OAuth 1.0 standard puts params in header
  :http_method        => :post,          # Request Tokens must be POST
  :request_token_path => "/oauth/request_token",
  :access_token_path  => "/oauth/access_token",
  :authorize_path     => "/oauth/authorize",
  :ssl                => { :verify_mode => OpenSSL::SSL::VERIFY_NONE },
  :no_verify          => true
})

# EXECUTE
begin
  puts "\n[ACTION] Requesting Token..."
  
  # The gem handles the nonce, timestamp, and signature automatically
  request_token = consumer.get_request_token(:oauth_callback => "oob")

  puts "\n[SUCCESS] 🚀 Server Responded!"
  puts "   > OAuth Token:  #{request_token.token}"
  puts "   > OAuth Secret: #{request_token.secret}"

rescue OAuth::Unauthorized => e
  puts "\n[FAILURE] 401 Unauthorized"
  puts "The server rejected the key or signature."
  puts "Raw Response: #{e.response.body}" if e.respond_to?(:response)
rescue Faraday::ConnectionFailed => e
  puts "\n[FAILURE] Connection Failed"
  puts "Is the Docker container running?"
rescue StandardError => e
  puts "\n[FAILURE] Error: #{e.class}"
  puts e.message
  puts e.backtrace
end


