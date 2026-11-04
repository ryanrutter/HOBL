// Copyright (c) Microsoft. All rights reserved.
// Licensed under the MIT license. See LICENSE file in the project root for full license information.

package com.microsoft.hobl.certinstaller

import java.io.InputStream
import java.security.cert.CertificateFactory
import java.security.cert.X509Certificate

object CertificateBundle {
    const val ROOT_CERT = "web_replay_root.pem"
    const val INTERMEDIATE_CERT = "web_replay_intermediate.pem"
    val certificateFiles = listOf(ROOT_CERT, INTERMEDIATE_CERT)

    fun decode(input: InputStream): X509Certificate =
        input.use {
            CertificateFactory.getInstance("X.509").generateCertificate(it) as X509Certificate
        }
}
