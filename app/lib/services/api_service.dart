import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

class ApiService extends ChangeNotifier {
  final String _baseUrl =
      'http://10.0.2.2:8000/api/v1'; // Android emulator localhost alias
  final String _wsUrl = 'ws://10.0.2.2:8000/api/v1/ws/dashboard';

  String? _token;
  String? get token => _token;
  WebSocketChannel? _channel;

  Map<String, dynamic> currentSensorData = {
    'soil_moisture': 0.0,
    'rainfall': 0.0,
    'temperature': 0.0,
    'vibration': 0.0,
    'tilt': 0.0,
    'humidity': 0.0,
  };

  Map<String, dynamic> currentPrediction = {
    'risk_score': 0.0,
    'risk_level': 'Safe',
    'timestamp': '',
  };

  // Auth Methods
  Future<bool> login(String phone, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone_number': phone,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _token = data['access_token'];
        notifyListeners();
        return true;
      }
    } catch (e) {
      debugPrint("Login error: $e");
    }
    return false;
  }

  // WebSocket for Real-Time Data
  void connectWebSocket() {
    _channel = WebSocketChannel.connect(Uri.parse(_wsUrl));
    _channel!.stream.listen((message) {
      final data = jsonDecode(message);
      if (data != null && data['sensor_data'] != null) {
        currentSensorData = data['sensor_data'];
        currentPrediction = data['prediction'];
        notifyListeners();
      }
    }, onError: (error) {
      debugPrint("WebSocket Error: $error");
    });
  }

  void disconnectWebSocket() {
    _channel?.sink.close();
  }
}
