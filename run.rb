require 'parallel'
require 'thor'
require 'octokit'
require 'csv'
require 'faraday-http-cache'

STDOUT.sync = true
class AnyGithubLoader < Thor
  desc 'load', 'Load github repository e.g. ruby run.rb load -t issue,pr,content -e README.md rails/rails'
  option :types, aliases: '-t', type: :array, desc: 'List in load types(issue, pr, content)', default: %w[issue pr]
  option :file_pattern, aliases: '-e', type: :string, desc: 'File pattern to load', default: 'README.md'
  def load(repo_name)
    contents = options[:types].map do |type|
      case type
      when 'issue'
        write_to_csv(client.issues(repo_name).map(&:body))
        write_to_csv(client.issues_comments(repo_name).map(&:body))
      when 'pr'
        write_to_csv(client.pull_requests(repo_name).map(&:body))
        write_to_csv(client.pull_requests_comments(repo_name).map(&:body))
      when 'content'
        file_pattern = options[:file_pattern]
        default_branch = client.repo(repo_name).default_branch

        target_files = client.tree(
          repo_name,
          default_branch,
          recursive: true
        )[:tree].select { |obj| obj[:type] == 'blob' && obj[:path] =~ /#{file_pattern}/ }

        target_files.each_slice(15) do |files|
          write_to_csv(Parallel.map(files, in_threads: 2) do |f|
            puts "target file: #{f[:path]}"
            Base64.decode64(client.contents(repo_name, ref: default_branch, path: f[:path])[:content])
          end)
        end
      end
    end.flatten
  end

  no_commands do
    def client
      unless @_octokit
        @_octokit = Octokit::Client.new(
          api_endpoint: ENV['GITHUB_API'] || 'https://api.github.com',
          access_token: ENV['GITHUB_TOKEN'],
          auto_paginate: true,
          per_page: 100
        )
        stack = Faraday::RackBuilder.new do |builder|
          builder.use Faraday::HttpCache, serializer: Marshal, shared_cache: false
          builder.use Octokit::Response::RaiseError
          builder.adapter Faraday.default_adapter
        end
        Octokit.middleware = stack
      end
      @_octokit
    end

    # メモリを使いたくないので小出しに書く
    def write_to_csv(contents)
      CSV.open('contents.csv', 'a') do |csv|
        contents.each do |content|
          csv << [content]
        end
      end
    end
  end
end

AnyGithubLoader.start(ARGV)
