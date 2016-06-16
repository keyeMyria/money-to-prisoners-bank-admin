/* jshint node: true */

var webpack = require('webpack');

module.exports = {
  entry: {
    app: './mtp_bank_admin/assets-src/javascripts/main.js'
  },
  output: {
    path: './mtp_bank_admin/assets/javascripts',
    filename: '[name].bundle.js'
  },
  module: {
    loaders: [
      { include: /\.json$/, loaders: ['json-loader'] }
    ],
    noParse: [
      /\.\/node_modules\/checked-polyfill\/checked-polyfill\.js$/
    ]
  },
  resolve: {
    root: [
      __dirname + '/node_modules'
    ],
    modulesDirectories: [
      'node_modules',
      'node_modules/money-to-prisoners-common/assets/javascripts/modules'
    ],
    extensions: ['', '.json', '.js']
  },
  plugins: [
    new webpack.optimize.DedupePlugin(),
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery'
    })
  ]
};
