# Chapter 5: ROS 2 Services and Actions

## Services (Request-Response)

Services provide synchronous request-response communication.

```python
from example_interfaces.srv import AddTwoInts

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')
        self.client = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        return self.client.call_async(request)
```

## Actions

Actions support long-running tasks with:
- Goal specification
- Periodic feedback
- Cancellation support
