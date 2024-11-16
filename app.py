import os
from dstack_sdk import AsyncTappdClient, DeriveKeyResponse, TdxQuoteResponse
from fastapi import FastAPI
from verify import verify_training_main
from deletemequote import Quote
import hashlib

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "The World! Call /derivekey or /tdxquote"}

@app.get("/derivekey")
async def derivekey():
    client = AsyncTappdClient()
    deriveKey = await client.derive_key('/', 'test')
    assert isinstance(deriveKey, DeriveKeyResponse)
    asBytes = deriveKey.toBytes()
    assert isinstance(asBytes, bytes)
    limitedSize = deriveKey.toBytes(32)
    return {"deriveKey": asBytes.hex(), "derive_32bytes": limitedSize.hex()}
    
@app.get("/tdxquote")
async def tdxquote():
    client = AsyncTappdClient()
    tdxQuote = await client.tdx_quote('test')
    assert isinstance(tdxQuote, TdxQuoteResponse)
    return {"tdxQuote": tdxQuote}

@app.get("/tdxquote_verbose")
async def tdxquote_verbose():
    client = AsyncTappdClient()
    tdxQuote = await client.tdx_quote('Verification passed_7408315c2c41fec8e93562fec1b85509e66ea82e7b1860de9338a7de23a95b1f')
    _, report = Quote.safeParse(bytes.fromhex(tdxQuote.quote[2:]))
    print("report", report.dict())
    assert isinstance(tdxQuote, TdxQuoteResponse)
    return {"tdxQuote": tdxQuote}

@app.get('/verifyPol')
async def verifyPol():
    client = AsyncTappdClient()
    verification_passed = verify_training_main()
    with open('proof/CIFAR10_test/hash.txt') as f:
        dataset_hash = f.read()

    if verification_passed:
        message = 'Verification passed' + '_' + dataset_hash
        tdxQuote = await client.tdx_quote(message)
        # reportData = 0xdfeb9480eff92e7138f1dc753bacda973a0c8cbe23e6f4ef98fb696118b99cc61ce525e2a6f49a2fee22bdadd80ac243c0f5365f3aa55ff9bdcc91a0cdc5fd52
        return {"message": "Verification passed", "tdxQuote": tdxQuote}

    return {"message": "Verification failed"}
