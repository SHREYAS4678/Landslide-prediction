import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import 'dart:async';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    final apiService = Provider.of<ApiService>(context, listen: false);
    // Try to connect to WS.
    apiService.connectWebSocket();
    
    // Simulate data ingestion (normally done by hardware sensors)
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      // Send mock ingestion call to trigger WS updates if running locally.
      // E.g. http.post to /api/v1/sensor-data ...
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    Provider.of<ApiService>(context, listen: false).disconnectWebSocket();
    super.dispose();
  }

  Color _getRiskColor(String riskLevel) {
    switch (riskLevel) {
      case "Safe":
        return Colors.green;
      case "Warning":
        return Colors.orange;
      case "High Risk":
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildSensorCard(String title, String value, IconData icon) {
    return Card(
      color: Colors.black45,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: Colors.amberAccent),
            const SizedBox(height: 10),
            Text(title, style: const TextStyle(fontSize: 14, color: Colors.white70)),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final apiService = Provider.of<ApiService>(context);
    final sensorData = apiService.currentSensorData;
    final prediction = apiService.currentPrediction;
    
    final riskLevel = prediction['risk_level'];
    final riskScore = prediction['risk_score'] as double;
    final riskColor = _getRiskColor(riskLevel);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Live Monitoring"),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacementNamed(context, '/'),
          )
        ],
      ),
      backgroundColor: Colors.black87,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Risk Status Header
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: riskColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: riskColor, width: 2),
                ),
                child: Column(
                  children: [
                    Text(
                      "CURRENT RISK: $riskLevel",
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: riskColor),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      "Risk Score: ${(riskScore * 100).toStringAsFixed(1)}%",
                      style: const TextStyle(fontSize: 18, color: Colors.white),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      "Last updated: ${DateTime.now().toString().substring(11, 19)}",
                      style: const TextStyle(fontSize: 12, color: Colors.white54),
                    )
                  ],
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                "Sensor Readings", 
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)
              ),
              const SizedBox(height: 16),
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    _buildSensorCard("Soil Moisture", "${sensorData['soil_moisture'].toStringAsFixed(2)}%", Icons.water_drop),
                    _buildSensorCard("Rainfall", "${sensorData['rainfall'].toStringAsFixed(1)} mm/hr", Icons.cloudy_snowing),
                    _buildSensorCard("Vibration", "${sensorData['vibration'].toStringAsFixed(3)} g", Icons.vibration),
                    _buildSensorCard("Tilt Angle", "${sensorData['tilt'].toStringAsFixed(1)}°", Icons.architecture),
                    _buildSensorCard("Temperature", "${sensorData['temperature'].toStringAsFixed(1)}°C", Icons.thermostat),
                    _buildSensorCard("Humidity", "${sensorData['humidity'].toStringAsFixed(1)}%", Icons.water),
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
