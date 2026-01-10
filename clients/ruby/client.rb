require 'oauth'
require 'openssl'
require 'net/http'
require 'cgi'

# CONFIGURATION
SITE_URL = "https://127.0.0.1.nip.io:9090"
CONSUMER_KEY    = "ClientKeyMustBeLongEnough00001"
CONSUMER_SECRET = "ClientSecretMustBeLongEnough01"

puts "--- RUBY CLIENT (FULL FLOW) ---"
puts "Target: #{SITE_URL}"

# Setup Consumer
# We disable peer verification because the Docker container uses a self-signed cert.
consumer = OAuth::Consumer.new(CONSUMER_KEY, CONSUMER_SECRET, {
  :site               => SITE_URL,
  :scheme             => :header,
  :http_method        => :post,
  :request_token_path => "/oauth/request_token",
  :access_token_path  => "/oauth/access_token",
  :authorize_path     => "/oauth/authorize",
  :ssl                => { :verify_mode => OpenSSL::SSL::VERIFY_NONE },
  :no_verify          => true
})

# GET REQUEST TOKEN
puts "\n[STEP 1] Requesting Temporary Token..."

# We use a manual request here to apply two specific fixes for strict servers:
# - Force a simple numeric nonce (Ruby defaults to complex Base64).
# - Remove 'Content-Type' header (Ruby sends it for empty bodies; Python hates it).
safe_nonce = rand(10 ** 30).to_s
options = { :oauth_callback => "oob", :nonce => safe_nonce }

req = consumer.create_signed_request(:post, "/oauth/request_token", nil, options)
req.delete("Content-Type") 

# Send the request manually
http = Net::HTTP.new(URI(SITE_URL).host, URI(SITE_URL).port)
http.use_ssl = true
http.verify_mode = OpenSSL::SSL::VERIFY_NONE
res = http.request(req)

if res.code != "200"
  abort "[FAILURE] Server returned #{res.code}: #{res.body}"
end

# Rehydrate the Token Object from the response
token_hash = CGI.parse(res.body)
request_token = OAuth::RequestToken.new(consumer, token_hash['oauth_token'][0], token_hash['oauth_token_secret'][0])

puts "   > Token:  #{request_token.token}"
puts "   > Secret: #{request_token.secret}"

# USER AUTHORIZATION
puts "\n[STEP 2] User Authorization"
puts "   > ---------------------------------------------------------"
puts "   > OPEN THIS URL IN YOUR BROWSER:"
puts "   > #{request_token.authorize_url}"
puts "   > ---------------------------------------------------------"
puts "   (The server will show you a 6-digit PIN code. Enter it below.)"

print "   > PIN Code: "
verifier = gets.chomp.strip

# GET ACCESS TOKEN
puts "\n[STEP 3] Exchanging for Access Token..."

begin
  access_token = request_token.get_access_token(:oauth_verifier => verifier)

  puts "\n[SUCCESS] 🚀 OAuth Flow Complete!"
  puts "   > FINAL Access Token:  #{access_token.token}"
  puts "   > FINAL Access Secret: #{access_token.secret}"
  puts "   > You can now use this token to access protected API endpoints."

rescue OAuth::Unauthorized => e
  puts "\n[FAILURE] ❌ The server rejected the code."
  puts "   > Response: #{e.request.body}"
rescue StandardError => e
  puts "\n[FAILURE] ❌ Error: #{e.message}"
end