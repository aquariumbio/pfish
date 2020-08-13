# frozen_string_literal: true

class ProtocolTest < ProtocolTestBase
  def setup
    add_random_operations(1)
  end

  def analyze
    log('Hello from Nemo')
    assert_equal(@backtrace.last[:operation], 'complete')
  end
end


