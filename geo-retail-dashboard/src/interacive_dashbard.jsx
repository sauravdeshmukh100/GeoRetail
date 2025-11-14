import React, { useState } from 'react';
import { MapPin, TrendingUp, Users, Store, Navigation, Award, BarChart3, AlertCircle } from 'lucide-react';

const GeoRetailDashboard = () => {
  const [selectedLocation, setSelectedLocation] = useState(null);

  // Top 10 locations data from your analysis
  const topLocations = [
    { rank: 1, score: 65.6, popDensity: 78046, competition: 25, amenities: 11.9, class: 'Very Good' },
    { rank: 2, score: 61.2, popDensity: 72483, competition: 0, amenities: 6.3, class: 'Very Good' },
    { rank: 3, score: 61.0, popDensity: 74363, competition: 0, amenities: 2.9, class: 'Very Good' },
    { rank: 4, score: 56.9, popDensity: 59914, competition: 15, amenities: 9.3, class: 'Good' },
    { rank: 5, score: 56.1, popDensity: 62044, competition: 0, amenities: 3.6, class: 'Good' },
    { rank: 6, score: 55.2, popDensity: 24481, competition: 78, amenities: 35.6, class: 'Good' },
    { rank: 7, score: 53.8, popDensity: 22835, competition: 12, amenities: 18.1, class: 'Good' },
    { rank: 8, score: 53.8, popDensity: 26449, competition: 61, amenities: 24.4, class: 'Good' },
    { rank: 9, score: 53.5, popDensity: 50896, competition: 0, amenities: 6.3, class: 'Good' },
    { rank: 10, score: 53.3, popDensity: 20596, competition: 17, amenities: 23.5, class: 'Good' }
  ];

  const projectStats = {
    totalCells: 1802,
    coverage: 470.36,
    population: 1579442,
    meanScore: 28.49,
    topScore: 65.56,
    underservedCells: 104,
    underservedPop: 666115,
    highCompetitionCells: 175,
    noRetailCells: 1266
  };

  const getClassColor = (classType) => {
    const colors = {
      'Very Good': 'bg-green-100 text-green-800 border-green-300',
      'Good': 'bg-blue-100 text-blue-800 border-blue-300',
      'Excellent': 'bg-purple-100 text-purple-800 border-purple-300',
      'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Low': 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[classType] || colors['Moderate'];
  };

  const getScoreColor = (score) => {
    if (score >= 60) return 'text-green-600';
    if (score >= 50) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-indigo-600">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                🎯 GeoRetail - Coimbatore Site Selection
              </h1>
              <p className="text-gray-600">
                Data-Driven Retail Location Analysis | Multi-Criteria Suitability Assessment
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Analysis Date</div>
              <div className="text-lg font-semibold">Sep 30, 2025</div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm font-medium">Coverage Area</div>
              <MapPin className="w-5 h-5 text-indigo-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{projectStats.coverage} km²</div>
            <div className="text-xs text-gray-500 mt-1">{projectStats.totalCells.toLocaleString()} grid cells analyzed</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm font-medium">Total Population</div>
              <Users className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{(projectStats.population / 1000000).toFixed(2)}M</div>
            <div className="text-xs text-gray-500 mt-1">Peak density: 78k/km²</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm font-medium">Market Opportunities</div>
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{projectStats.underservedCells}</div>
            <div className="text-xs text-gray-500 mt-1">{(projectStats.underservedPop / 1000).toFixed(0)}k underserved population</div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <div className="text-gray-600 text-sm font-medium">Top Suitability Score</div>
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{projectStats.topScore}/100</div>
            <div className="text-xs text-gray-500 mt-1">Mean: {projectStats.meanScore}</div>
          </div>
        </div>
      </div>

      {/* Market Insights */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-6 border border-green-200">
            <div className="flex items-center mb-3">
              <div className="bg-green-600 rounded-full p-2 mr-3">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-bold text-green-900">High Opportunity</h3>
            </div>
            <div className="text-3xl font-bold text-green-900 mb-2">{projectStats.noRetailCells}</div>
            <p className="text-sm text-green-700">Cells with NO retail presence - massive white space for market entry</p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-6 border border-blue-200">
            <div className="flex items-center mb-3">
              <div className="bg-blue-600 rounded-full p-2 mr-3">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-bold text-blue-900">Population Hotspots</h3>
            </div>
            <div className="text-3xl font-bold text-blue-900 mb-2">339</div>
            <p className="text-sm text-blue-700">Cells with {'>'}5,000 people/km² showing strong market demand</p>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow p-6 border border-orange-200">
            <div className="flex items-center mb-3">
              <div className="bg-orange-600 rounded-full p-2 mr-3">
                <Store className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-bold text-orange-900">Competitive Zones</h3>
            </div>
            <div className="text-3xl font-bold text-orange-900 mb-2">{projectStats.highCompetitionCells}</div>
            <p className="text-sm text-orange-700">Cells with {'>'}5 stores - saturated markets requiring differentiation</p>
          </div>
        </div>
      </div>

      {/* Top Locations Table */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
            <h2 className="text-xl font-bold text-white flex items-center">
              <Award className="w-6 h-6 mr-2" />
              Top 10 Recommended Retail Locations
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Population Density</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Competition</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amenities</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {topLocations.map((location) => (
                  <tr 
                    key={location.rank}
                    className={`hover:bg-gray-50 transition-colors ${
                      selectedLocation?.rank === location.rank ? 'bg-indigo-50' : ''
                    }`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className={`
                          inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-white
                          ${location.rank <= 3 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' : 
                            location.rank <= 5 ? 'bg-gradient-to-r from-gray-300 to-gray-500' : 
                            'bg-gradient-to-r from-orange-300 to-orange-500'}
                        `}>
                          {location.rank}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className={`text-xl font-bold ${getScoreColor(location.score)}`}>
                        {location.score}
                      </div>
                      <div className="text-xs text-gray-500">out of 100</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900">
                        {location.popDensity.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">people/km²</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Store className="w-4 h-4 mr-1 text-gray-400" />
                        <span className={`font-semibold ${
                          location.competition === 0 ? 'text-green-600' :
                          location.competition < 20 ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {location.competition}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500">
                        {location.competition === 0 ? 'No competition' :
                         location.competition < 20 ? 'Low-Medium' : 'High'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-gray-900">{location.amenities}</div>
                      <div className="text-xs text-gray-500">score</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getClassColor(location.class)}`}>
                        {location.class}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedLocation(location)}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center"
                      >
                        <BarChart3 className="w-4 h-4 mr-1" />
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Location Detail Modal */}
      {selectedLocation && (
        <div className="max-w-7xl mx-auto mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-indigo-200">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Location #{selectedLocation.rank} - Detailed Analysis
                </h3>
                <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${getClassColor(selectedLocation.class)}`}>
                  {selectedLocation.class}
                </span>
              </div>
              <button
                onClick={() => setSelectedLocation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                <div className="text-sm font-medium text-purple-700 mb-1">Overall Score</div>
                <div className="text-4xl font-bold text-purple-900">{selectedLocation.score}</div>
                <div className="text-xs text-purple-600 mt-1">Highly suitable for retail</div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                <div className="text-sm font-medium text-green-700 mb-1">Market Size</div>
                <div className="text-2xl font-bold text-green-900">{selectedLocation.popDensity.toLocaleString()}</div>
                <div className="text-xs text-green-600 mt-1">people/km² - {
                  selectedLocation.popDensity > 60000 ? 'Very High' :
                  selectedLocation.popDensity > 40000 ? 'High' :
                  selectedLocation.popDensity > 20000 ? 'Medium' : 'Moderate'
                } density</div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                <div className="text-sm font-medium text-blue-700 mb-1">Competition Level</div>
                <div className="text-2xl font-bold text-blue-900">{selectedLocation.competition}</div>
                <div className="text-xs text-blue-600 mt-1">
                  {selectedLocation.competition === 0 ? '✅ Zero competition - First mover advantage!' :
                   selectedLocation.competition < 20 ? '✅ Low-Medium competition - Good entry opportunity' :
                   '⚠️ High competition - Needs differentiation'}
                </div>
              </div>
            </div>

            <div className="mt-6 bg-gray-50 rounded-lg p-4">
              <h4 className="font-bold text-gray-900 mb-3 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-indigo-600" />
                Strategic Recommendation
              </h4>
              <ul className="space-y-2 text-sm text-gray-700">
                {selectedLocation.rank <= 5 ? (
                  <>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Priority Location:</strong> Immediate opportunity for market entry</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Market Size:</strong> {selectedLocation.popDensity > 60000 ? 'Very large' : 'Large'} customer base with high density</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      <span><strong>Competition:</strong> {selectedLocation.competition < 10 ? 'Minimal' : 'Manageable'} - favorable market conditions</span>
                    </li>
                  </>
                ) : (
                  <>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">•</span>
                      <span><strong>Secondary Opportunity:</strong> Consider after priority locations</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-blue-600 mr-2">•</span>
                      <span><strong>Strategy:</strong> Differentiated offering or specialized format</span>
                    </li>
                  </>
                )}
                <li className="flex items-start">
                  <span className="text-indigo-600 mr-2">→</span>
                  <span><strong>Next Steps:</strong> Field verification, real estate assessment, detailed market research</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Key Recommendations */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-6 flex items-center">
            <Navigation className="w-7 h-7 mr-3" />
            Strategic Action Plan
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white bg-opacity-10 rounded-lg p-5 backdrop-blur-sm">
              <div className="text-yellow-300 font-bold mb-2">🎯 PRIORITY 1</div>
              <h3 className="font-bold text-lg mb-2">Immediate Opportunities</h3>
              <p className="text-sm text-indigo-100">
                Target locations #1-#5 for immediate market entry. High population, low competition, excellent potential.
              </p>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-5 backdrop-blur-sm">
              <div className="text-green-300 font-bold mb-2">🚀 PRIORITY 2</div>
              <h3 className="font-bold text-lg mb-2">Market Gap Expansion</h3>
              <p className="text-sm text-indigo-100">
                104 underserved locations with 666k population. Zero to minimal competition - prime for growth.
              </p>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-5 backdrop-blur-sm">
              <div className="text-blue-300 font-bold mb-2">⭐ PRIORITY 3</div>
              <h3 className="font-bold text-lg mb-2">Competitive Entry</h3>
              <p className="text-sm text-indigo-100">
                Locations #6-#10 in established markets. Require differentiation strategy and superior execution.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeoRetailDashboard;