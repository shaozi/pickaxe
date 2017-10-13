const Web3 = require('web3')
const { exec } = require('child_process')
const { StringDecoder } = require('string_decoder');
const decoder = new StringDecoder('utf8');

var web3 = new Web3()
web3.setProvider(new web3.providers.HttpProvider('http://localhost:8545'))
/*
var coinbase = web3.eth.coinbase
console.log(coinbase)
var balance = web3.eth.getBalance(coinbase)
console.log("Balance: ", balance)
var isMining = web3.eth.mining
console.log("Mining: ", isMining)
*/
// async calls use this
//var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'))
var lastBalance = 0
var lastHashrate = 0
var timesOfRestart = 0
function padString(str, length, pad) {
  pad = pad || ' '
  length = length || 80
  var strLength = str.length
  var diff = length - str.length
  if (diff < 0) return str
  var padLength = Math.floor(diff/2)
  var retStr = ''
  for (var i = 0; i < padLength; i++) {
    retStr += pad
  }
  retStr += str
  for (var i = 0; i < padLength + diff%2; i++) {
    retStr += pad
  }
  return retStr
}

function wait(sec) {
  return new Promise(function(resolve, reject) {
    setTimeout(function() { resolve() }, sec * 1000)
  })
}

function check(web3) {
  return web3.eth.getCoinbase().then(coinbase => {
    return web3.eth.getBalance(coinbase)
  }).then(balance => {
    if (balance > lastBalance) {
      console.log(padString('*', 80, '*'))
      console.log(`*${padString(' YOU HAVE NEW COIN ', 78, '*')}*`)
      let balanceInfoString = `${lastBalance} -> ${balance}`
      console.log(`*${padString(balanceInfoString, 78, '*')}*`)
      console.log(padString('*', 80, '*'))
    }
    lastBalance = balance
    return web3.eth.getHashrate()
  }).then(hashrate => {
    console.log(`hashrate = ${hashrate}`)
    var delta = hashrate - lastHashrate
    lastHashrate = hashrate
    if (hashrate == 0 || delta < -40000000) {
        
      if (++timeOfRestart >= 5) {
        timeOfRestart = 0
        console.log(`!!!!!!!!!! Restarted ${timeOfRestart} times and still hashrate == 0 !!!!!!!!!!`)
      }
      lastHashrate = 0
      console.log("---- Miner stops working ----")
      console.log("---- Stop Miner and wait for 2 minutes ----")
      exec('systemctl stop miner')
      return wait(120).then(() => {
        console.log("---- Start Miner ----")
        exec('systemctl start miner')
        return wait(60)
      })
    } 
    timeOfRestart = 0
    return wait(60)
  }).then(() => {
    check(web3)
  }).catch(error => {
    console.error(error)
    return wait(60).then(() => {
      throw (new Error('Failed and exit!'))
    })
  })
}

console.log(padString('', 80, '*'))
console.log(`*${padString('', 78)}*`)
console.log(`*${padString("Check Miner Scheduler started", 78)}*`)
console.log(`*${padString('', 78)}*`)
console.log(padString('', 80, '*'))
check(web3)

