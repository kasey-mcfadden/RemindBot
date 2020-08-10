require 'sinatra'
set :bind, '0.0.0.0'
set :port, 5000

post '/notifications' do
  puts request.body.read
end
