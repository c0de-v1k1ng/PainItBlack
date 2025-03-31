import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const WeightHistoryGraph = () => {
  const [weightData, setWeightData] = useState([]);
  const [minWeight, setMinWeight] = useState(0);
  const [maxWeight, setMaxWeight] = useState(1);

  useEffect(() => {
    // Find the element that contains our weight data JSON
    const dataElement = document.getElementById('weight_data_json');

    if (dataElement && dataElement.textContent) {
      try {
        const data = JSON.parse(dataElement.textContent);

        // Process the data for the chart
        const formattedData = data.map(record => ({
          date: record.date,
          weight: parseFloat(record.weight)
        }));

        setWeightData(formattedData);

        // Calculate min and max weights for better Y axis scaling
        if (formattedData.length > 0) {
          const weights = formattedData.map(item => item.weight);
          const min = Math.min(...weights);
          const max = Math.max(...weights);

          // Add a bit of padding (10%) to the min/max for better visualization
          const padding = (max - min) * 0.1;
          setMinWeight(Math.max(0, min - padding)); // Ensure min is not below 0
          setMaxWeight(max + padding);
        }
      } catch (error) {
        console.error("Error parsing weight data:", error);
      }
    }
  }, []);

  // Don't render if we don't have enough data
  if (weightData.length < 2) {
    return <div>Insufficient weight data for graph</div>;
  }

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={weightData}
          margin={{
            top: 5,
            right: 20,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            padding={{ left: 10, right: 10 }}
          />
          <YAxis
            domain={[minWeight, maxWeight]}
            label={{ value: 'Weight (kg)', angle: -90, position: 'insideLeft' }}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value) => [`${value.toFixed(1)} kg`, 'Weight']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="weight"
            name="Weight (kg)"
            stroke="#4f46e5"
            strokeWidth={2}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WeightHistoryGraph;