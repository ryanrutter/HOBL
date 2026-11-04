// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.certinstaller

import android.app.Activity
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.os.Bundle
import android.util.Log

class InstallCaActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val requestId = intent.getStringExtra(EXTRA_REQUEST_ID) ?: "missing"
        val operation = intent.getStringExtra(EXTRA_OPERATION) ?: OP_INSTALL
        val message = try {
            runOperation(operation)
        } catch (e: Exception) {
            Log.e(TAG, "Certificate operation failed for request $requestId", e)
            "ERROR: ${e.message ?: e.javaClass.simpleName}"
        }

        Log.i(TAG, "RESULT:$requestId:$message")
        setResult(if (message.startsWith("OK:")) RESULT_OK else RESULT_CANCELED)
        finish()
    }

    private fun runOperation(operation: String): String {
        require(operation == OP_INSTALL || operation == OP_UNINSTALL) {
            "Unsupported operation: $operation"
        }
        val policy = getSystemService(DevicePolicyManager::class.java)
            ?: error("DevicePolicyManager is unavailable")
        check(policy.isProfileOwnerApp(packageName)) {
            "HOBL certificate installer is not the profile owner for this Android user"
        }

        val admin = ComponentName(this, HoblDeviceAdminReceiver::class.java)
        val results = CertificateBundle.certificateFiles.map { fileName ->
            val certificate = assets.open(fileName).use(CertificateBundle::decode).encoded
            val installed = policy.hasCaCertInstalled(admin, certificate)
            if (operation == OP_INSTALL) {
                if (!installed) {
                    check(policy.installCaCert(admin, certificate)) {
                        "Android did not install $fileName"
                    }
                }
                "$fileName=${if (installed) "present" else "installed"}"
            } else {
                if (installed) policy.uninstallCaCert(admin, certificate)
                "$fileName=${if (installed) "removed" else "absent"}"
            }
        }
        return "OK:${results.joinToString(",")}"
    }

    companion object {
        const val EXTRA_REQUEST_ID = "com.microsoft.hobl.certinstaller.REQUEST_ID"
        const val EXTRA_OPERATION = "com.microsoft.hobl.certinstaller.OPERATION"
        const val OP_INSTALL = "install"
        const val OP_UNINSTALL = "uninstall"
        const val TAG = "HoblCertInstaller"
    }
}
