import { IDmissionTokenGenerator } from "idmission-auth-client";

const token = await new IDmissionTokenGenerator().generate()

const accessToken = token.access_token;
console.log("token: ", accessToken)
