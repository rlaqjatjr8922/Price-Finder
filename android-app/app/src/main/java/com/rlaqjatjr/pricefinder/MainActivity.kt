package com.rlaqjatjr.pricefinder

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val queryInput = findViewById<EditText>(R.id.queryInput)

        fun openSearch(urlTemplate: String) {
            val query = queryInput.text.toString().trim()
            if (query.isEmpty()) {
                Toast.makeText(this, "검색어를 입력하세요.", Toast.LENGTH_SHORT).show()
                return
            }
            val encoded = URLEncoder.encode(query, StandardCharsets.UTF_8.toString())
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(urlTemplate.format(encoded))))
        }

        findViewById<Button>(R.id.naverButton).setOnClickListener {
            openSearch("https://search.shopping.naver.com/search/all?query=%s")
        }
        findViewById<Button>(R.id.daangnButton).setOnClickListener {
            openSearch("https://www.daangn.com/kr/buy-sell/?search=%s")
        }
        findViewById<Button>(R.id.joonggonaraButton).setOnClickListener {
            openSearch("https://web.joongna.com/search/%s")
        }
        findViewById<Button>(R.id.bunjangButton).setOnClickListener {
            openSearch("https://m.bunjang.co.kr/search/products?q=%s")
        }
    }
}
